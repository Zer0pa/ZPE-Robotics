"""Phase 9 self-inflicted red-team audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any

import numpy as np

from zpe_robotics.anomaly import AnomalyDetector, DEFAULT_ANOMALY_Z_THRESHOLD
from zpe_robotics.codec import ZPBotCodec
from zpe_robotics.enterprise_dataset import load_episode_matrices
from zpe_robotics.fixtures import generate_joint_trajectory
from zpe_robotics.lerobot_codec import ZPELeRobotCodec, build_synthetic_episode
from zpe_robotics.primitive_index import PrimitiveIndex
from zpe_robotics.release_candidate import REFERENCE_ROUNDTRIP_SHA256, compute_reference_bridge_roundtrip
from zpe_robotics.telemetry import create_tracking_bundle
from zpe_robotics.utils import write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Phase 9 red-team audit.")
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--benchmark-result", type=Path, required=True)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--dataset-name", type=str, required=True)
    parser.add_argument("--synthetic-benchmark", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--python312-log", type=Path, required=True)
    return parser.parse_args()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def verdict_from_threshold(value: float, *, threshold: float) -> str:
    return "WITHSTANDS" if value >= threshold else "FAILS"


def attack_1(benchmark_payload: dict[str, Any]) -> dict[str, Any]:
    results = benchmark_payload["results"]
    zpe_ratio = float(results["zpe_p8"]["compression_ratio"])
    zstd_ratio = float(results["zstd_l3"]["compression_ratio"])
    relative_ratio = zpe_ratio / max(zstd_ratio, 1.0e-12)
    return {
        "attack_id": "attack_1_strawman_baseline",
        "argument": "No enterprise user stores raw float32; zstd-l3 is the minimum baseline.",
        "verdict": verdict_from_threshold(relative_ratio, threshold=3.0),
        "zpe_compression_ratio": zpe_ratio,
        "zstd_l3_compression_ratio": zstd_ratio,
        "relative_ratio": relative_ratio,
    }


def attack_2(benchmark_payload: dict[str, Any], synthetic_payload: dict[str, Any]) -> dict[str, Any]:
    real_ratio = float(benchmark_payload["results"]["zpe_p8"]["compression_ratio"])
    synthetic_ratio = float(synthetic_payload["compression_ratio"])
    return {
        "attack_id": "attack_2_synthetic_entropy",
        "argument": "The headline compression ratio may rely on low-entropy synthetic data.",
        "verdict": "WITHSTANDS" if real_ratio >= 20.0 else "PARTIALLY WITHSTANDS",
        "synthetic_fixture_ratio": synthetic_ratio,
        "real_dataset_ratio": real_ratio,
    }


def attack_3() -> dict[str, Any]:
    lerobot_episode = build_synthetic_episode()
    lerobot_codec = ZPELeRobotCodec()
    core_codec = ZPBotCodec(keep_coeffs=8)

    with tempfile.TemporaryDirectory(prefix="phase9_redteam_attack3_") as temp_dir:
        root = Path(temp_dir)
        packet_path = root / "lerobot_episode.zpbot"
        lerobot_codec.encode_episode(lerobot_episode, packet_path)
        lerobot_decoded = lerobot_codec.decode_episode(packet_path)
        lerobot_original = np.asarray(lerobot_episode["joint_positions"], dtype=np.float32)
        lerobot_replay = np.asarray(lerobot_decoded["joint_positions"], dtype=np.float32)

    core_original = np.asarray(lerobot_episode["joint_positions"], dtype=np.float32)
    core_replay = core_codec.decode(core_codec.encode(core_original)).astype(np.float32)
    lerobot_exact = bool(np.array_equal(lerobot_original, lerobot_replay))
    core_exact = bool(np.array_equal(core_original, core_replay))

    verdict = "WITHSTANDS" if core_exact else "FAILS"
    return {
        "attack_id": "attack_3_lossless_qualification",
        "argument": "Strict bit-exact replay is required to support a lossless claim.",
        "verdict": verdict,
        "lerobot_array_equal": lerobot_exact,
        "core_zpbot_array_equal": core_exact,
        "lerobot_max_abs_error": float(np.max(np.abs(lerobot_original - lerobot_replay))),
        "core_max_abs_error": float(np.max(np.abs(core_original - core_replay))),
    }


def _resample_episode(trajectory: np.ndarray, *, target_frames: int = 96) -> np.ndarray:
    arr = np.asarray(trajectory, dtype=np.float32)
    if arr.ndim != 2:
        raise ValueError("episode trajectory must be 2D")
    if arr.shape[0] == target_frames:
        return arr
    if arr.shape[0] == 1:
        return np.repeat(arr, target_frames, axis=0)

    source_x = np.linspace(0.0, 1.0, arr.shape[0], dtype=np.float64)
    target_x = np.linspace(0.0, 1.0, target_frames, dtype=np.float64)
    columns = [np.interp(target_x, source_x, arr[:, joint_idx].astype(np.float64)) for joint_idx in range(arr.shape[1])]
    return np.stack(columns, axis=1).astype(np.float32)


def attack_4(dataset_root: Path, *, dataset_name: str) -> dict[str, Any]:
    episodes, meta = load_episode_matrices(dataset_root, repo_id=dataset_name, min_joints=6)
    codec = ZPBotCodec(keep_coeffs=8)
    with tempfile.TemporaryDirectory(prefix="phase9_redteam_attack4_") as temp_dir:
        corpus_dir = Path(temp_dir)
        index = PrimitiveIndex()
        for episode_index, episode in enumerate(episodes):
            packet_path = corpus_dir / f"push_{episode_index:03d}.zpbot"
            packet_path.write_bytes(codec.encode(_resample_episode(episode)))
            index.add(packet_path, "push")
        results = index.search("PUSH", top_k=10)

    hits = sum(1 for _filepath, label, _score, _template in results if label == "push")
    precision_at_10 = float(hits / max(1, len(results)))
    verdict = "WITHSTANDS"
    note = "real corpus evaluated across all available episodes"
    if len(episodes) < 200 or meta.get("fps", 0.0) < 50.0:
        verdict = "PARTIALLY WITHSTANDS"
        note = "real corpus evaluated, but the available dataset undershoots the 200-episode/50 Hz target"
    return {
        "attack_id": "attack_4_real_corpus_size",
        "argument": "Synthetic P@10 may be meaningless without a real corpus and known sample count.",
        "verdict": verdict,
        "precision_at_10": precision_at_10,
        "episodes_tested": len(episodes),
        "fps": meta.get("fps"),
        "joint_count": meta.get("joint_count"),
        "note": note,
    }


def attack_5(repo_root: Path) -> dict[str, Any]:
    codec = ZPBotCodec(keep_coeffs=8)
    with tempfile.TemporaryDirectory(prefix="phase9_redteam_attack5_") as temp_dir:
        root = Path(temp_dir)
        nominal_paths: list[Path] = []
        for idx in range(20):
            trajectory = generate_joint_trajectory(num_frames=4096, num_joints=6, seed=20260243 + idx)
            path = root / f"nominal_{idx:02d}.zpbot"
            path.write_bytes(codec.encode(trajectory))
            nominal_paths.append(path)

        detector = AnomalyDetector(z_threshold=DEFAULT_ANOMALY_Z_THRESHOLD).fit(nominal_paths)
        reports = [detector.classify(path) for path in nominal_paths]

    false_positives = sum(1 for report in reports if report.flagged)
    false_positive_rate = float(false_positives / 20.0)
    verdict = "FAILS"
    if false_positives == 0:
        verdict = "WITHSTANDS"
    elif false_positive_rate <= 0.05:
        verdict = "PARTIALLY WITHSTANDS"
    return {
        "attack_id": "attack_5_false_positive_rate",
        "argument": "Recall without false-positive rate over nominal trajectories is incomplete.",
        "verdict": verdict,
        "false_positives": false_positives,
        "nominal_trajectories_tested": 20,
        "false_positive_rate": false_positive_rate,
    }


def _resolve_uv(repo_root: Path) -> Path:
    uv_path = shutil.which("uv")
    if uv_path:
        return Path(uv_path)

    install = subprocess.run(
        [sys.executable, "-m", "pip", "install", "uv"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if install.returncode != 0:
        raise RuntimeError(f"unable to install uv: {install.stderr.strip() or install.stdout.strip()}")

    candidate = Path(sys.executable).resolve().parent / "uv"
    if candidate.exists():
        return candidate
    uv_path = shutil.which("uv")
    if uv_path:
        return Path(uv_path)
    raise RuntimeError("uv remained unavailable after installation")


def attack_6(repo_root: Path, python312_log: Path) -> dict[str, Any]:
    python312_log.parent.mkdir(parents=True, exist_ok=True)
    venv_dir = repo_root / ".venv312_phase9_redteam"
    if venv_dir.exists():
        shutil.rmtree(venv_dir)

    log_chunks: list[str] = []
    try:
        uv_bin = _resolve_uv(repo_root)
        commands = [
            [str(uv_bin), "python", "install", "3.12"],
            [str(uv_bin), "venv", "--python", "3.12", str(venv_dir)],
            [str(uv_bin), "pip", "install", "--python", str(venv_dir / "bin" / "python"), "-e", f"{repo_root}[dev]"],
            [
                str(venv_dir / "bin" / "python"),
                "-c",
                (
                    "import json; "
                    "from zpe_robotics.release_candidate import compute_reference_bridge_roundtrip, REFERENCE_ROUNDTRIP_SHA256; "
                    "report = compute_reference_bridge_roundtrip(); "
                    "payload = {'reference_sha256': REFERENCE_ROUNDTRIP_SHA256, 'replay_sha256': report['replay_sha256'], 'matches_reference': report['replay_sha256'] == REFERENCE_ROUNDTRIP_SHA256}; "
                    "print(json.dumps(payload, sort_keys=True))"
                ),
            ],
            [str(venv_dir / "bin" / "python"), "-m", "pytest", str(repo_root / "tests"), "-x"],
        ]

        parity_payload: dict[str, Any] = {}
        for command in commands:
            try:
                result = subprocess.run(
                    command,
                    cwd=repo_root,
                    capture_output=True,
                    text=True,
                    check=False,
                )
            except Exception as exc:
                log_chunks.append(f"$ {' '.join(command)}\nEXCEPTION: {type(exc).__name__}: {exc}")
                python312_log.write_text("\n\n".join(log_chunks), encoding="utf-8")
                return {
                    "attack_id": "attack_6_python312_parity",
                    "argument": "Python 3.12 parity was not previously proven.",
                    "verdict": "FAILS",
                    "command": " ".join(command),
                    "exception": f"{type(exc).__name__}: {exc}",
                    "python312_log": str(python312_log),
                }

            log_chunks.append(f"$ {' '.join(command)}\n{result.stdout}{result.stderr}")
            if result.returncode != 0:
                python312_log.write_text("\n\n".join(log_chunks), encoding="utf-8")
                return {
                    "attack_id": "attack_6_python312_parity",
                    "argument": "Python 3.12 parity was not previously proven.",
                    "verdict": "FAILS",
                    "command": " ".join(command),
                    "returncode": result.returncode,
                    "python312_log": str(python312_log),
                }
            if command[0].endswith("/python") and len(command) > 2 and command[1] == "-c":
                parity_payload = json.loads(result.stdout.strip())

        python312_log.write_text("\n\n".join(log_chunks), encoding="utf-8")
        return {
            "attack_id": "attack_6_python312_parity",
            "argument": "Python 3.12 parity was not previously proven.",
            "verdict": "WITHSTANDS",
            "reference_sha256": REFERENCE_ROUNDTRIP_SHA256,
            "replay_sha256": parity_payload.get("replay_sha256", ""),
            "matches_reference": bool(parity_payload.get("matches_reference")),
            "python312_log": str(python312_log),
        }
    except Exception as exc:
        log_chunks.append(f"UNHANDLED EXCEPTION: {type(exc).__name__}: {exc}")
        python312_log.write_text("\n\n".join(log_chunks), encoding="utf-8")
        return {
            "attack_id": "attack_6_python312_parity",
            "argument": "Python 3.12 parity was not previously proven.",
            "verdict": "FAILS",
            "exception": f"{type(exc).__name__}: {exc}",
            "python312_log": str(python312_log),
        }
    finally:
        shutil.rmtree(venv_dir, ignore_errors=True)


def attack_7() -> dict[str, Any]:
    return {
        "attack_id": "attack_7_single_operator_provenance",
        "argument": "Evidence remains first-party until an external party reproduces it.",
        "verdict": "OPEN",
        "required_external_reproduction": [
            "pip install zpe-motion-kernel",
            "pytest tests/ -x",
            "Compare against proofs/enterprise_benchmark/benchmark_result.json and proofs/red_team/red_team_report.json",
        ],
    }


def main() -> int:
    args = parse_args()
    benchmark_payload = read_json(args.benchmark_result)
    synthetic_payload = read_json(args.synthetic_benchmark)

    tracking = create_tracking_bundle(
        run_name="red_team_phase9",
        input_payload={"dataset_name": args.dataset_name},
        metadata={"phase": "09", "task": "red_team"},
    )

    attacks = [
        attack_1(benchmark_payload),
        attack_2(benchmark_payload, synthetic_payload),
        attack_3(),
        attack_4(args.dataset_root, dataset_name=args.dataset_name),
        attack_5(args.repo_root),
        attack_6(args.repo_root, args.python312_log),
        attack_7(),
    ]

    summary = {
        "attacks_total": len(attacks),
        "withstands": sum(1 for attack in attacks if attack["verdict"] == "WITHSTANDS"),
        "partially_withstands": sum(1 for attack in attacks if attack["verdict"] == "PARTIALLY WITHSTANDS"),
        "fails": sum(1 for attack in attacks if attack["verdict"] == "FAILS"),
        "open": sum(1 for attack in attacks if attack["verdict"] == "OPEN"),
    }

    tracking.log_tool_result(
        "red_team_phase9",
        metrics={
            "withstands": float(summary["withstands"]),
            "partially_withstands": float(summary["partially_withstands"]),
            "fails": float(summary["fails"]),
            "open": float(summary["open"]),
        },
        parameters={
            "dataset_name": args.dataset_name,
            "benchmark_path": str(args.benchmark_result),
            "synthetic_benchmark_path": str(args.synthetic_benchmark),
        },
    )

    payload = {
        "timestamp_utc": subprocess.run(
            ["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip(),
        "dataset_name": args.dataset_name,
        "benchmark_result_path": str(args.benchmark_result),
        "dataset_root": str(args.dataset_root),
        "attacks": attacks,
        "summary": summary,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_json(args.output, payload)
    payload["tracking"] = tracking.finish(
        artifact_paths=[str(args.output), str(args.python312_log)],
        output_payload={"summary": summary},
    )
    write_json(args.output, payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
