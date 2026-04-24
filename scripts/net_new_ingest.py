#!/usr/bin/env python
"""Appendix D/E maximalization and NET-NEW ingestion pipeline."""

from __future__ import annotations

# ruff: noqa: E402

import argparse
import datetime as dt
import hashlib
import json
import os
import platform
import subprocess
import sys
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from datasets import load_dataset
from huggingface_hub import HfApi

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from zpe_robotics.constants import ALLOWED_IMP_CODES, RUNPOD_DEFERMENT_ARTIFACTS
from zpe_robotics.runtime_probe import probe_ros2_moveit as runtime_probe_ros2_moveit
from zpe_robotics.utils import ensure_dir, write_json, write_text

os.environ.setdefault("HF_HUB_ENABLE_HF_TRANSFER", "0")


@dataclass
class CmdResult:
    command: str
    returncode: int
    stdout: str
    stderr: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run NET-NEW resource ingestion")
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260220)
    parser.add_argument("--sample-size", type=int, default=128)
    return parser.parse_args()


def _run_cmd(command: list[str], timeout: int = 120, env: dict[str, str] | None = None) -> CmdResult:
    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=timeout, env=env)
        return CmdResult(
            command=" ".join(command),
            returncode=proc.returncode,
            stdout=(proc.stdout or "").strip(),
            stderr=(proc.stderr or "").strip(),
        )
    except FileNotFoundError as exc:
        return CmdResult(
            command=" ".join(command),
            returncode=127,
            stdout="",
            stderr=f"{type(exc).__name__}: {exc}",
        )
    except subprocess.TimeoutExpired as exc:
        return CmdResult(
            command=" ".join(command),
            returncode=124,
            stdout=(exc.stdout or "").strip() if isinstance(exc.stdout, str) else "",
            stderr=(exc.stderr or "").strip() if isinstance(exc.stderr, str) else "timeout",
        )


def _short(text: str, limit: int = 240) -> str:
    return text if len(text) <= limit else text[:limit]


def _cmd_record(result: CmdResult) -> dict[str, Any]:
    return {
        "command": result.command,
        "returncode": result.returncode,
        "stdout": _short(result.stdout, 600),
        "stderr": _short(result.stderr, 600),
    }


def _append_attempts_log(lines: list[str], attempts: list[CmdResult]) -> None:
    for idx, item in enumerate(attempts, start=1):
        lines.append(f"- attempt_{idx}_command: `{item.command}`")
        lines.append(f"- attempt_{idx}_returncode: {item.returncode}")
        if item.returncode != 0:
            lines.append(f"- attempt_{idx}_error: {_short(item.stderr or item.stdout)}")


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        key = k.strip()
        val = v.strip()
        if (val.startswith("\"") and val.endswith("\"")) or (val.startswith("'") and val.endswith("'")):
            val = val[1:-1]
        os.environ.setdefault(key, val)


def _flatten_numeric(value: Any) -> np.ndarray:
    if value is None:
        return np.array([], dtype=np.float64)
    if isinstance(value, np.ndarray):
        return value.astype(np.float64, copy=False).reshape(-1)
    if isinstance(value, (list, tuple)):
        if not value:
            return np.array([], dtype=np.float64)
        arrs = [_flatten_numeric(v) for v in value]
        if not arrs:
            return np.array([], dtype=np.float64)
        return np.concatenate(arrs) if arrs else np.array([], dtype=np.float64)
    if isinstance(value, (int, float)):
        return np.array([float(value)], dtype=np.float64)
    return np.array([], dtype=np.float64)


def _sample_stream(dataset: Any, sample_size: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    it = iter(dataset)
    for _ in range(sample_size):
        try:
            rows.append(next(it))
        except StopIteration:
            break
    return rows


def _numeric_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    action_vecs: list[np.ndarray] = []
    state_vecs: list[np.ndarray] = []
    task_idxs: list[int] = []

    for row in rows:
        action = _flatten_numeric(row.get("action"))
        if action.size == 0:
            action = _flatten_numeric(row.get("observation.action"))
        state = _flatten_numeric(row.get("observation.state"))
        if action.size > 0:
            action_vecs.append(action)
        if state.size > 0:
            state_vecs.append(state)
        task = row.get("task_index")
        if isinstance(task, (int, np.integer)):
            task_idxs.append(int(task))

    if not action_vecs:
        return {
            "samples": len(rows),
            "numeric_samples": 0,
            "compression_ratio_estimate": 0.0,
            "action_dim_mean": 0.0,
            "state_dim_mean": 0.0,
            "action_energy_mean": 0.0,
            "task_diversity": 0,
        }

    action_dim_mean = float(np.mean([a.size for a in action_vecs]))
    state_dim_mean = float(np.mean([s.size for s in state_vecs])) if state_vecs else 0.0
    action_energy_mean = float(np.mean([float(np.linalg.norm(a)) for a in action_vecs]))
    packed = b"".join(a.astype(np.float32, copy=False).tobytes(order="C") for a in action_vecs)
    compressed = zlib.compress(packed, level=9)
    ratio = float(len(packed) / max(1, len(compressed)))

    return {
        "samples": len(rows),
        "numeric_samples": len(action_vecs),
        "compression_ratio_estimate": ratio,
        "action_dim_mean": action_dim_mean,
        "state_dim_mean": state_dim_mean,
        "action_energy_mean": action_energy_mean,
        "task_diversity": int(len(set(task_idxs))),
    }


def _build_policy_dataset(rows: list[dict[str, Any]], source_name: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        action = _flatten_numeric(row.get("action"))
        if action.size == 0:
            action = _flatten_numeric(row.get("observation.action"))
        task = row.get("task_index")
        if action.size < 4 or not isinstance(task, (int, np.integer)):
            continue
        out.append({"source": source_name, "label": int(task), "action": action})
    return out


def _policy_features_naive(action: np.ndarray) -> np.ndarray:
    bins = np.linspace(-2.5, 2.5, 17)
    hist = np.histogram(np.clip(action, -2.5, 2.5), bins=bins)[0].astype(np.float64)
    norm = np.sum(hist)
    return hist / max(norm, 1.0)


def _policy_features_zpe(action: np.ndarray) -> np.ndarray:
    delta = np.diff(action)
    if delta.size == 0:
        return np.zeros(8, dtype=np.float64)
    sign = np.sign(delta)
    sign_map = sign + 1
    mag = np.abs(delta)
    q1, q2 = np.quantile(mag, [0.33, 0.66])
    mag_bin = np.digitize(mag, [q1, q2], right=False)
    token = sign_map.astype(np.int64) * 3 + np.clip(mag_bin.astype(np.int64), 0, 2)
    hist = np.bincount(token, minlength=9).astype(np.float64)
    norm = np.sum(hist)
    return hist / max(norm, 1.0)


def _centroid_accuracy(dataset: list[dict[str, Any]], feature_fn: Any) -> float:
    by_label: dict[int, list[np.ndarray]] = {}
    for item in dataset:
        by_label.setdefault(item["label"], []).append(item["action"])

    filtered = {label: rows for label, rows in by_label.items() if len(rows) >= 3}
    labels = sorted(filtered)
    if len(labels) < 2:
        return 0.0

    train: list[tuple[int, np.ndarray]] = []
    test: list[tuple[int, np.ndarray]] = []
    for label in labels:
        rows = filtered[label]
        split = max(1, int(0.7 * len(rows)))
        train.extend((label, r) for r in rows[:split])
        test.extend((label, r) for r in rows[split:])

    centroids: dict[int, np.ndarray] = {}
    for label in labels:
        feats = [feature_fn(r) for label_id, r in train if label_id == label]
        centroids[label] = np.mean(np.stack(feats, axis=0), axis=0)

    correct = 0
    for label, row in test:
        feat = feature_fn(row)
        pred = max(
            labels,
            key=lambda x: float(
                np.dot(centroids[x], feat)
                / max(np.linalg.norm(centroids[x]) * np.linalg.norm(feat), 1.0e-12)
            ),
        )
        if pred == label:
            correct += 1
    return float(correct / max(1, len(test)))


def _impracticality(
    resource: str,
    code: str,
    command: str,
    error_signature: str,
    fallback: str,
    claim_impact_note: str,
) -> dict[str, Any]:
    if code not in ALLOWED_IMP_CODES:
        raise ValueError(f"invalid impracticality code: {code}")
    return {
        "resource": resource,
        "code": code,
        "command": command,
        "error_signature": error_signature,
        "fallback": fallback,
        "claim_impact_note": claim_impact_note,
    }


def _pick_arm64_python() -> tuple[str | None, list[CmdResult]]:
    attempts: list[CmdResult] = []
    candidates = ["/opt/homebrew/bin/python3.11", "python3.11", "python3"]
    probe = "import platform,sys; print(platform.machine()); print(sys.version.split()[0])"
    for candidate in candidates:
        result = _run_cmd([candidate, "-c", probe], timeout=20)
        attempts.append(result)
        if result.returncode != 0:
            continue
        lines = [x.strip() for x in result.stdout.splitlines() if x.strip()]
        if len(lines) < 2:
            continue
        machine, version = lines[0], lines[1]
        if machine == "arm64" and version.startswith("3.11"):
            return candidate, attempts
    return None, attempts


def _arm64_tools_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PATH"] = "/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
    return env


def _docker_daemon_unavailable(result: CmdResult) -> bool:
    text = f"{result.stdout}\n{result.stderr}".lower()
    return "cannot connect to the docker daemon" in text


def _ensure_docker_daemon(attempts: list[CmdResult]) -> None:
    colima_bin = "/opt/homebrew/bin/colima" if Path("/opt/homebrew/bin/colima").exists() else "colima"
    env = _arm64_tools_env()
    status = _run_cmd([colima_bin, "status"], timeout=40, env=env)
    attempts.append(status)
    if status.returncode == 0 and "running" in status.stdout.lower():
        return
    start = _run_cmd([colima_bin, "start", "--cpu", "4", "--memory", "8", "--disk", "60"], timeout=1200, env=env)
    attempts.append(start)


def _probe_ros2_moveit() -> dict[str, Any]:
    attempts: list[CmdResult] = []
    local_ros2 = _run_cmd(["ros2", "--version"], timeout=20)
    attempts.append(local_ros2)
    if local_ros2.returncode == 0:
        local_pkg = _run_cmd(["ros2", "pkg", "list"], timeout=40)
        attempts.append(local_pkg)
        if local_pkg.returncode == 0 and "moveit" in local_pkg.stdout.lower():
            return {
                "status": "PASS",
                "runtime_path": "local",
                "attempts": [_cmd_record(a) for a in attempts],
            }

    docker_bin = "/opt/homebrew/bin/docker" if Path("/opt/homebrew/bin/docker").exists() else "docker"
    docker_check = _run_cmd([docker_bin, "--version"], timeout=20)
    attempts.append(docker_check)
    if docker_check.returncode == 0:
        docker_ros2 = _run_cmd(
            [
                docker_bin,
                "run",
                "--rm",
                "docker.io/library/ros:humble-ros-base-jammy",
                "bash",
                "-lc",
                "ros2 --help >/dev/null && echo ROS2_OK",
            ],
            timeout=120,
        )
        attempts.append(docker_ros2)
        if docker_ros2.returncode != 0 and _docker_daemon_unavailable(docker_ros2):
            _ensure_docker_daemon(attempts)
            docker_ros2 = _run_cmd(
                [
                    docker_bin,
                    "run",
                    "--rm",
                    "docker.io/library/ros:humble-ros-base-jammy",
                    "bash",
                    "-lc",
                    "ros2 --help >/dev/null && echo ROS2_OK",
                ],
                timeout=120,
                env=_arm64_tools_env(),
            )
            attempts.append(docker_ros2)
        if docker_ros2.returncode != 0:
            return {"status": "FAIL", "runtime_path": "none", "attempts": [_cmd_record(a) for a in attempts]}

        docker_moveit_prebuilt = _run_cmd(
            [
                docker_bin,
                "run",
                "--rm",
                "docker.io/moveit/moveit2:humble-source",
                "bash",
                "-lc",
                "ros2 pkg list | grep -i '^moveit' | head -n 1",
            ],
            timeout=180,
            env=_arm64_tools_env(),
        )
        attempts.append(docker_moveit_prebuilt)

        docker_moveit_runtime = docker_moveit_prebuilt
        if docker_moveit_prebuilt.returncode != 0:
            docker_moveit_runtime = _run_cmd(
                [
                    docker_bin,
                    "run",
                    "--rm",
                    "docker.io/library/ros:humble-ros-base-jammy",
                    "bash",
                    "-lc",
                    (
                        "set -e; "
                        "apt-get update -qq >/dev/null; "
                        "DEBIAN_FRONTEND=noninteractive apt-get install -y -qq ros-humble-moveit >/dev/null; "
                        "ros2 pkg list | grep -i '^moveit' | head -n 1"
                    ),
                ],
                timeout=1200,
                env=_arm64_tools_env(),
            )
            attempts.append(docker_moveit_runtime)

        if docker_ros2.returncode == 0 and docker_moveit_runtime.returncode == 0 and docker_moveit_runtime.stdout.strip():
            return {
                "status": "PASS",
                "runtime_path": "docker",
                "attempts": [_cmd_record(a) for a in attempts],
            }

    podman_bin = "/opt/homebrew/bin/podman" if Path("/opt/homebrew/bin/podman").exists() else "podman"
    podman_check = _run_cmd([podman_bin, "--version"], timeout=20)
    attempts.append(podman_check)
    if podman_check.returncode == 0:
        podman_start = _run_cmd([podman_bin, "machine", "start", "zpe-robotics-podman"], timeout=90)
        attempts.append(podman_start)
        if podman_start.returncode != 0:
            start_err = (podman_start.stderr or podman_start.stdout).lower()
            if "does not exist" in start_err or "no such machine" in start_err:
                podman_init = _run_cmd(
                    [
                        podman_bin,
                        "machine",
                        "init",
                        "--cpus",
                        "4",
                        "--memory",
                        "8192",
                        "--disk-size",
                        "60",
                        "zpe-robotics-podman",
                    ],
                    timeout=900,
                )
                attempts.append(podman_init)
                podman_start = _run_cmd([podman_bin, "machine", "start", "zpe-robotics-podman"], timeout=120)
                attempts.append(podman_start)
        podman_ros2 = _run_cmd(
            [podman_bin, "run", "--rm", "docker.io/library/ros:humble-ros-base-jammy", "ros2", "--version"],
            timeout=120,
        )
        attempts.append(podman_ros2)
        podman_moveit = _run_cmd(
            [
                podman_bin,
                "run",
                "--rm",
                "docker.io/moveit/moveit2:humble-source",
                "bash",
                "-lc",
                "ros2 pkg list | grep -i '^moveit' | head -n 1",
            ],
            timeout=180,
        )
        attempts.append(podman_moveit)
        if podman_ros2.returncode == 0 and podman_moveit.returncode == 0 and podman_moveit.stdout.strip():
            return {
                "status": "PASS",
                "runtime_path": "podman",
                "attempts": [_cmd_record(a) for a in attempts],
            }

    return {"status": "FAIL", "runtime_path": "none", "attempts": [_cmd_record(a) for a in attempts]}


def _probe_octo() -> dict[str, Any]:
    attempts: list[CmdResult] = []
    hf_home = str(ROOT / ".hf_cache_octo")
    python_cmds: list[tuple[str, str, str]] = [
        (
            sys.executable,
            "rail-berkeley/octo-base",
            "from octo.model.octo_model import OctoModel; OctoModel.load_pretrained('hf://rail-berkeley/octo-base'); print('OCTO_OK')",
        ),
    ]
    octo_venv_python = ROOT / ".venv_octo_arm64" / "bin" / "python"
    if octo_venv_python.exists():
        python_cmds.append(
            (
                str(octo_venv_python),
                "rail-berkeley/octo-small",
                "from octo.model.octo_model import OctoModel; OctoModel.load_pretrained('hf://rail-berkeley/octo-small'); print('OCTO_OK')",
            )
        )

    for py_bin, model_id, code in python_cmds:
        env = dict(os.environ)
        env["HF_HOME"] = hf_home
        env["HF_HUB_ENABLE_HF_TRANSFER"] = "0"
        try:
            proc = subprocess.run([py_bin, "-c", code], capture_output=True, text=True, timeout=420, env=env)
            result = CmdResult(
                command=f"HF_HOME={hf_home} {py_bin} -c {code} # model={model_id}",
                returncode=proc.returncode,
                stdout=(proc.stdout or "").strip(),
                stderr=(proc.stderr or "").strip(),
            )
        except FileNotFoundError as exc:
            result = CmdResult(
                command=f"HF_HOME={hf_home} {py_bin} -c {code} # model={model_id}",
                returncode=127,
                stdout="",
                stderr=f"{type(exc).__name__}: {exc}",
            )
        except subprocess.TimeoutExpired as exc:
            result = CmdResult(
                command=f"HF_HOME={hf_home} {py_bin} -c {code} # model={model_id}",
                returncode=124,
                stdout=(exc.stdout or "").strip() if isinstance(exc.stdout, str) else "",
                stderr=(exc.stderr or "").strip() if isinstance(exc.stderr, str) else "timeout",
            )

        attempts.append(result)
        if result.returncode == 0 and "OCTO_OK" in result.stdout:
            return {
                "status": "PASS",
                "attempts": [_cmd_record(a) for a in attempts],
                "selected_python": py_bin,
                "selected_model": model_id,
                "error_signature": "",
            }

    last = attempts[-1] if attempts else CmdResult(command="OCTO_PROBE", returncode=1, stdout="", stderr="no attempts")
    return {
        "status": "FAIL",
        "attempts": [_cmd_record(a) for a in attempts],
        "selected_python": "",
        "selected_model": "",
        "error_signature": _short(last.stderr or last.stdout),
    }


def _probe_mujoco(args: argparse.Namespace, out: Path) -> dict[str, Any]:
    attempts: list[CmdResult] = []
    parity_output = out / "mujoco_parity_report.json"
    selected_python = sys.executable

    local_import_cmd = [sys.executable, "-c", "import mujoco; print('MUJOCO_OK', mujoco.__version__)"]
    local_import = _run_cmd(local_import_cmd, timeout=40)
    attempts.append(local_import)

    if local_import.returncode == 0:
        parity_cmd = [
            sys.executable,
            str(ROOT / "scripts" / "mujoco_parity_probe.py"),
            "--output",
            str(parity_output),
            "--seed",
            str(args.seed),
            "--samples",
            str(args.sample_size),
        ]
        parity_run = _run_cmd(parity_cmd, timeout=240)
        attempts.append(parity_run)
        if parity_run.returncode == 0 and parity_output.exists():
            report = json.loads(parity_output.read_text(encoding="utf-8"))
            return {
                "status": "PASS" if report.get("status") == "PASS" else "FAIL",
                "selected_python": selected_python,
                "parity_report": report,
                "attempts": [_cmd_record(a) for a in attempts],
            }

    arm64_python, python_probe_attempts = _pick_arm64_python()
    attempts.extend(python_probe_attempts)

    if arm64_python is None:
        return {
            "status": "FAIL",
            "selected_python": selected_python,
            "parity_report": {},
            "attempts": [_cmd_record(a) for a in attempts],
        }

    venv_dir = ROOT / ".venv_mujoco_arm64"
    venv_python = venv_dir / "bin" / "python"
    selected_python = str(venv_python)

    create_venv = _run_cmd([arm64_python, "-m", "venv", str(venv_dir)], timeout=120)
    attempts.append(create_venv)
    if create_venv.returncode != 0:
        return {
            "status": "FAIL",
            "selected_python": selected_python,
            "parity_report": {},
            "attempts": [_cmd_record(a) for a in attempts],
        }

    pip_upgrade = _run_cmd(
        [str(venv_python), "-m", "pip", "install", "-q", "--upgrade", "pip", "setuptools", "wheel"],
        timeout=180,
    )
    attempts.append(pip_upgrade)
    pip_install = _run_cmd(
        [str(venv_python), "-m", "pip", "install", "-q", "mujoco==3.5.0", "--only-binary=:all:"],
        timeout=240,
    )
    attempts.append(pip_install)
    if pip_install.returncode != 0:
        return {
            "status": "FAIL",
            "selected_python": selected_python,
            "parity_report": {},
            "attempts": [_cmd_record(a) for a in attempts],
        }

    parity_cmd = [
        str(venv_python),
        str(ROOT / "scripts" / "mujoco_parity_probe.py"),
        "--output",
        str(parity_output),
        "--seed",
        str(args.seed),
        "--samples",
        str(args.sample_size),
    ]
    parity_run = _run_cmd(parity_cmd, timeout=240)
    attempts.append(parity_run)

    report = {}
    if parity_output.exists():
        report = json.loads(parity_output.read_text(encoding="utf-8"))

    return {
        "status": "PASS" if parity_run.returncode == 0 and report.get("status") == "PASS" else "FAIL",
        "selected_python": selected_python,
        "parity_report": report,
        "attempts": [_cmd_record(a) for a in attempts],
    }


def _build_runpod_lock(sys_python: str) -> str:
    freeze = _run_cmd([sys_python, "-m", "pip", "--version"], timeout=30)
    freeze_sig = _short(freeze.stdout or freeze.stderr, 500)
    lines = [
        "# RunPod dependency lock (generated in-lane)",
        f"# local_pip_signature: {freeze_sig}",
        "# Target runtime: Linux + Python 3.11 + NVIDIA GPU",
        "numpy==1.26.4",
        "datasets==4.5.0",
        "huggingface_hub==1.4.1",
        "pyarrow==23.0.0",
        "pandas==2.2.3",
        "h5py==3.11.0",
        "tensorflow==2.15.1",
        "tensorflow-probability==0.23.0",
        "jax==0.4.31",
        "jaxlib==0.4.31",
        "flax==0.10.4",
        "mujoco==3.5.0",
        "octo @ git+https://github.com/octo-models/octo.git@main",
    ]
    return "\n".join(lines) + "\n"


def _final_gap_status(
    resolved: bool,
    imp_code: str | None,
    has_commercial_open_alternative: bool,
) -> str:
    if resolved:
        return "RESOLVED"
    if imp_code in {"IMP-LICENSE", "IMP-ACCESS"} and not has_commercial_open_alternative:
        return "PAUSED_EXTERNAL"
    return "FAIL"


def _e1_lock_inputs() -> list[Path]:
    env_root = os.environ.get("ZPE_NET_NEW_PACK_ROOT")
    candidates: list[Path] = []
    if env_root:
        base = Path(env_root)
        candidates.extend(
            [
                base / "ZPE 10-Lane NET-NEW Resource Maximization Pack.md",
                base / "ZPE 10-Lane NET-NEW Resource Maximization Pack.pdf",
            ]
        )
    candidates.extend(
        [
            ROOT / "reference_material" / "ZPE 10-Lane NET-NEW Resource Maximization Pack.md",
            ROOT / "reference_material" / "ZPE 10-Lane NET-NEW Resource Maximization Pack.pdf",
        ]
    )
    return candidates


def main() -> None:
    args = parse_args()
    out = args.output_root
    ensure_dir(out)
    _load_env_file(ROOT / ".env")

    api = HfApi()
    impractical: list[dict[str, Any]] = []
    validation_lines: list[str] = ["# Max Resource Validation Log", ""]

    # E1 lock inputs
    e1_paths = _e1_lock_inputs()
    e1_inputs = []
    for p in e1_paths:
        if p.exists():
            e1_inputs.append({"path": str(p), "size_bytes": p.stat().st_size, "sha256": _sha256_file(p)})
        else:
            impractical.append(
                _impracticality(
                    resource="NET-NEW pack input",
                    code="IMP-ACCESS",
                    command=f"ls -l {p}",
                    error_signature="file not found",
                    fallback="use PRD Appendix E text only",
                    claim_impact_note="NET-NEW pack missing; closure evidence reduced.",
                )
            )

    resource_index = {
        "agibot_primary": ("dataset", "agibot-world/AgiBotWorld-Beta"),
        "agibot_fallback": ("dataset", "weijian-sun/agibotworld-lerobot"),
        "openx_primary": ("dataset", "jxu124/OpenX-Embodiment"),
        "openx_fallback": ("dataset", "IVC-liuyuan/Swift-OpenX-Embodiment-action-chunk-jsons"),
        "rh20t": ("dataset", "hainh22/rh20t"),
        "lerobot": ("dataset", "lerobot/svla_so101_pickplace"),
        "libero": ("dataset", "whosricky/libero_spatial_v30"),
        "octo": ("model", "rail-berkeley/octo-base"),
    }

    resource_lock: dict[str, Any] = {
        "generated_at": dt.datetime.now(dt.UTC).isoformat(),
        "seed": args.seed,
        "deterministic_sampling_policy": "first_n_rows_streaming",
        "runtime": {"python": platform.python_version(), "platform": platform.platform()},
        "e1_inputs": e1_inputs,
        "resources": {},
    }
    for key, (kind, rid) in resource_index.items():
        try:
            info = api.dataset_info(rid) if kind == "dataset" else api.model_info(rid)
            resource_lock["resources"][key] = {
                "kind": kind,
                "id": rid,
                "sha": info.sha,
                "gated": getattr(info, "gated", None),
                "sibling_count": len(getattr(info, "siblings", []) or []),
            }
        except Exception as exc:
            resource_lock["resources"][key] = {
                "kind": kind,
                "id": rid,
                "status": "metadata_failed",
                "error": f"{type(exc).__name__}: {str(exc)[:300]}",
            }

    # AgiBot attempts
    agibot_rows: list[dict[str, Any]] = []
    agibot_primary_cmd = "load_dataset('agibot-world/AgiBotWorld-Beta', split='train', streaming=True)"
    validation_lines.extend(["## AgiBot World", f"- primary_command: `{agibot_primary_cmd}`"])
    try:
        ds = load_dataset("agibot-world/AgiBotWorld-Beta", split="train", streaming=True)
        _ = next(iter(ds))
        validation_lines.append("- primary_result: PASS")
    except Exception as exc:
        msg = f"{type(exc).__name__}: {str(exc)[:240]}"
        validation_lines.append(f"- primary_result: FAIL ({msg})")
        impractical.append(
            _impracticality(
                resource="AgiBot World",
                code="IMP-ACCESS",
                command=agibot_primary_cmd,
                error_signature=msg,
                fallback="Use weijian-sun/agibotworld-lerobot deterministic subset",
                claim_impact_note="Official AgiBot gated access unavailable; fallback path used.",
            )
        )

    agibot_fallback_uri = (
        "hf://datasets/weijian-sun/agibotworld-lerobot/task_327/data/chunk-000/episode_000000.parquet"
    )
    agibot_fallback_cmd = (
        "load_dataset('parquet', data_files={'train':['"
        + agibot_fallback_uri
        + "']}, split='train', streaming=True)"
    )
    validation_lines.append(f"- fallback_command: `{agibot_fallback_cmd}`")
    try:
        ds = load_dataset("parquet", data_files={"train": [agibot_fallback_uri]}, split="train", streaming=True)
        agibot_rows = _sample_stream(ds, args.sample_size)
        validation_lines.append(f"- fallback_result: PASS (samples={len(agibot_rows)})")
    except Exception as exc:
        msg = f"{type(exc).__name__}: {str(exc)[:240]}"
        validation_lines.append(f"- fallback_result: FAIL ({msg})")
        impractical.append(
            _impracticality(
                resource="AgiBot World fallback",
                code="IMP-NOCODE",
                command=agibot_fallback_cmd,
                error_signature=msg,
                fallback="No additional fallback available",
                claim_impact_note="AgiBot-linked claims fail because no readable fallback was available.",
            )
        )
    agibot_metrics = _numeric_metrics(agibot_rows)

    # OpenX attempts
    validation_lines.extend(["", "## Open X-Embodiment"])
    openx_rows: list[dict[str, Any]] = []
    openx_primary_cmd = "load_dataset('jxu124/OpenX-Embodiment', split='train', streaming=True)"
    validation_lines.append(f"- primary_command: `{openx_primary_cmd}`")
    try:
        ds = load_dataset("jxu124/OpenX-Embodiment", split="train", streaming=True)
        _ = next(iter(ds))
        validation_lines.append("- primary_result: PASS")
    except Exception as exc:
        msg = f"{type(exc).__name__}: {str(exc)[:240]}"
        validation_lines.append(f"- primary_result: FAIL ({msg})")
        impractical.append(
            _impracticality(
                resource="Open X-Embodiment",
                code="IMP-NOCODE",
                command=openx_primary_cmd,
                error_signature=msg,
                fallback="Use IVC-liuyuan/Swift-OpenX-Embodiment-action-chunk-jsons",
                claim_impact_note="Primary OpenX loader path unavailable in current datasets runtime.",
            )
        )

    openx_fallback_cmd = "load_dataset('IVC-liuyuan/Swift-OpenX-Embodiment-action-chunk-jsons', split='train', streaming=True)"
    validation_lines.append(f"- fallback_command: `{openx_fallback_cmd}`")
    try:
        ds = load_dataset("IVC-liuyuan/Swift-OpenX-Embodiment-action-chunk-jsons", split="train", streaming=True)
        openx_rows = _sample_stream(ds, args.sample_size)
        validation_lines.append(f"- fallback_result: PASS (samples={len(openx_rows)})")
    except Exception as exc:
        msg = f"{type(exc).__name__}: {str(exc)[:240]}"
        validation_lines.append(f"- fallback_result: FAIL ({msg})")
        impractical.append(
            _impracticality(
                resource="OpenX fallback",
                code="IMP-ACCESS",
                command=openx_fallback_cmd,
                error_signature=msg,
                fallback="No additional fallback available",
                claim_impact_note="OpenX-linked cross-embodiment closure fails due unavailable fallback.",
            )
        )
    openx_metrics = {
        "samples": len(openx_rows),
        "avg_messages_per_sample": float(np.mean([len(r.get("messages", [])) for r in openx_rows]) if openx_rows else 0.0),
        "avg_images_per_sample": float(np.mean([len(r.get("images", [])) for r in openx_rows]) if openx_rows else 0.0),
    }

    # RH20T attempts
    validation_lines.extend(["", "## RH20T"])
    rh20t_rows: list[dict[str, Any]] = []
    rh20t_cmd = "load_dataset('hainh22/rh20t', split='train', streaming=True)"
    validation_lines.append(f"- command: `{rh20t_cmd}`")
    try:
        ds = load_dataset("hainh22/rh20t", split="train", streaming=True)
        rh20t_rows = _sample_stream(ds, args.sample_size)
        validation_lines.append(f"- result: PASS (samples={len(rh20t_rows)})")
    except Exception as exc:
        msg = f"{type(exc).__name__}: {str(exc)[:240]}"
        validation_lines.append(f"- result: FAIL ({msg})")
        impractical.append(
            _impracticality(
                resource="RH20T",
                code="IMP-ACCESS",
                command=rh20t_cmd,
                error_signature=msg,
                fallback="No fallback available",
                claim_impact_note="RH20T stress evidence path failed due inaccessible resource.",
            )
        )
    rh20t_metrics = _numeric_metrics(rh20t_rows)

    # LeRobot + LIBERO direct
    validation_lines.extend(["", "## LeRobot Direct Run"])
    lerobot_rows: list[dict[str, Any]] = []
    lerobot_cmd = "load_dataset('lerobot/svla_so101_pickplace', split='train', streaming=True)"
    validation_lines.append(f"- command: `{lerobot_cmd}`")
    try:
        ds = load_dataset("lerobot/svla_so101_pickplace", split="train", streaming=True)
        lerobot_rows = _sample_stream(ds, args.sample_size)
        validation_lines.append(f"- result: PASS (samples={len(lerobot_rows)})")
    except Exception as exc:
        msg = f"{type(exc).__name__}: {str(exc)[:240]}"
        validation_lines.append(f"- result: FAIL ({msg})")
        impractical.append(
            _impracticality(
                resource="LeRobot",
                code="IMP-ACCESS",
                command=lerobot_cmd,
                error_signature=msg,
                fallback="No fallback available",
                claim_impact_note="Direct LeRobot execution failed; D2 closure cannot pass.",
            )
        )

    validation_lines.extend(["", "## LIBERO Direct Run"])
    libero_rows: list[dict[str, Any]] = []
    libero_cmd = "load_dataset('whosricky/libero_spatial_v30', split='train', streaming=True)"
    validation_lines.append(f"- command: `{libero_cmd}`")
    try:
        ds = load_dataset("whosricky/libero_spatial_v30", split="train", streaming=True)
        libero_rows = _sample_stream(ds, args.sample_size)
        validation_lines.append(f"- result: PASS (samples={len(libero_rows)})")
    except Exception as exc:
        msg = f"{type(exc).__name__}: {str(exc)[:240]}"
        validation_lines.append(f"- result: FAIL ({msg})")
        impractical.append(
            _impracticality(
                resource="LIBERO",
                code="IMP-ACCESS",
                command=libero_cmd,
                error_signature=msg,
                fallback="No fallback available",
                claim_impact_note="Direct LIBERO execution failed; D2 closure cannot pass.",
            )
        )
    lerobot_metrics = _numeric_metrics(lerobot_rows)
    libero_metrics = _numeric_metrics(libero_rows)

    # M1 ROS2 + MoveIt runtime
    validation_lines.extend(["", "## ROS2 / MoveIt2 Runtime"])
    ros_probe = runtime_probe_ros2_moveit()
    ros_attempts = [CmdResult(**x) for x in ros_probe["attempts"]]
    _append_attempts_log(validation_lines, ros_attempts)
    validation_lines.append(f"- runtime_path: {ros_probe['runtime_path']}")
    validation_lines.append(f"- result: {ros_probe['status']}")
    write_json(
        out / "ros2_runtime_probe.json",
        {
            "generated_at": dt.datetime.now(dt.UTC).isoformat(),
            "status": ros_probe["status"],
            "runtime_path": ros_probe["runtime_path"],
            "attempts": ros_probe["attempts"],
            "pass_criteria": "ros2 executable and MoveIt package discovery through local or container runtime path",
        },
    )
    if ros_probe["status"] != "PASS":
        ros_last_error = ""
        for attempt in reversed(ros_probe["attempts"]):
            err = attempt.get("stderr") or attempt.get("stdout")
            if err:
                ros_last_error = _short(str(err))
                break
        impractical.append(
            _impracticality(
                resource="ROS2+MoveIt2 native runtime",
                code="IMP-NOCODE",
                command=" ; ".join([x["command"] for x in ros_probe["attempts"]]),
                error_signature=ros_last_error or "runtime path unavailable",
                fallback="in-lane rosbag callback simulation only",
                claim_impact_note="M1 fails: no native/containerized ROS2+MoveIt runtime path succeeded.",
            )
        )

    # M3 MuJoCo runtime parity
    validation_lines.extend(["", "## MuJoCo Runtime"])
    mujoco_probe = _probe_mujoco(args, out)
    mujoco_attempts = [CmdResult(**x) for x in mujoco_probe["attempts"]]
    _append_attempts_log(validation_lines, mujoco_attempts)
    validation_lines.append(f"- selected_python: {mujoco_probe['selected_python']}")
    validation_lines.append(f"- result: {mujoco_probe['status']}")
    write_json(
        out / "mujoco_runtime_probe.json",
        {
            "generated_at": dt.datetime.now(dt.UTC).isoformat(),
            "status": mujoco_probe["status"],
            "selected_python": mujoco_probe["selected_python"],
            "attempts": mujoco_probe["attempts"],
            "parity_report_path": "mujoco_parity_report.json",
        },
    )
    if mujoco_probe["status"] != "PASS":
        mu_last_error = ""
        for attempt in reversed(mujoco_probe["attempts"]):
            err = attempt.get("stderr") or attempt.get("stdout")
            if err:
                mu_last_error = _short(str(err))
                break
        impractical.append(
            _impracticality(
                resource="MuJoCo parity runtime",
                code="IMP-NOCODE",
                command=" ; ".join([x["command"] for x in mujoco_probe["attempts"]]),
                error_signature=mu_last_error or "mujoco parity runtime failed",
                fallback="analytic FK replay parity",
                claim_impact_note="M3 fails: MuJoCo runtime parity did not meet pass criteria.",
            )
        )

    # Octo policy comparator
    validation_lines.extend(["", "## Octo Policy Comparator"])
    octo_probe = _probe_octo()
    octo_attempts = [CmdResult(**x) for x in octo_probe["attempts"]]
    _append_attempts_log(validation_lines, octo_attempts)
    validation_lines.append(f"- selected_python: {octo_probe.get('selected_python','')}")
    octo_error = ""
    if octo_probe["status"] != "PASS":
        octo_error = _short(octo_probe.get("error_signature", "octo probe failed"))
        validation_lines.append(f"- result: FAIL ({octo_error})")
        impractical.append(
            _impracticality(
                resource="Octo policy comparator",
                code="IMP-COMPUTE",
                command=" ; ".join([x["command"] for x in octo_probe["attempts"]]) or "octo_probe",
                error_signature=octo_error,
                fallback="RunPod GPU path with pinned stack and deterministic command chain",
                claim_impact_note="Direct Octo comparator failed locally and remains FAIL until RunPod execution.",
            )
        )
    else:
        validation_lines.append("- result: PASS")

    # Cross-embodiment
    corpus_metrics = {
        "agibot_fallback": agibot_metrics,
        "rh20t": rh20t_metrics,
        "lerobot": lerobot_metrics,
        "libero": libero_metrics,
    }
    vectors: list[np.ndarray] = []
    vector_labels: list[str] = []
    for name, m in corpus_metrics.items():
        if m["numeric_samples"] <= 0:
            continue
        vec = np.array(
            [
                float(m["action_dim_mean"]),
                float(m["state_dim_mean"]),
                float(m["action_energy_mean"]),
                float(m["compression_ratio_estimate"]),
            ],
            dtype=np.float64,
        )
        vectors.append(vec)
        vector_labels.append(name)

    pairwise = []
    if len(vectors) >= 2:
        stack = np.stack(vectors, axis=0)
        norms = np.linalg.norm(stack, axis=1)
        for i in range(len(vectors)):
            for j in range(i + 1, len(vectors)):
                sim = float(np.dot(stack[i], stack[j]) / max(norms[i] * norms[j], 1.0e-12))
                pairwise.append({"a": vector_labels[i], "b": vector_labels[j], "cosine_similarity": sim})

    consistency_score = float(np.mean([p["cosine_similarity"] for p in pairwise])) if pairwise else 0.0
    cross_embodiment = {
        "generated_at": dt.datetime.now(dt.UTC).isoformat(),
        "corpus_metrics": corpus_metrics,
        "pairwise_similarity": pairwise,
        "consistency_score": consistency_score,
        "multi_embodiment_evidence": bool(len(vectors) >= 2),
        "status": "PASS" if len(vectors) >= 2 else "FAIL",
    }
    write_json(out / "cross_embodiment_consistency_report.json", cross_embodiment)

    # Policy proxy
    policy_rows = _build_policy_dataset(agibot_rows, "agibot") + _build_policy_dataset(rh20t_rows, "rh20t")
    naive_acc = _centroid_accuracy(policy_rows, _policy_features_naive)
    zpe_acc = _centroid_accuracy(policy_rows, _policy_features_zpe)
    policy_report = {
        "generated_at": dt.datetime.now(dt.UTC).isoformat(),
        "octo_model": octo_probe.get("selected_model", "rail-berkeley/octo-base"),
        "octo_inference_status": "PASS" if octo_probe["status"] == "PASS" else "FAIL",
        "octo_error_signature": octo_error,
        "proxy_dataset_samples": len(policy_rows),
        "proxy_naive_accuracy": float(naive_acc),
        "proxy_zpe_accuracy": float(zpe_acc),
        "proxy_delta": float(zpe_acc - naive_acc),
        "status": "PASS" if (octo_probe["status"] == "PASS" and zpe_acc >= naive_acc) else "FAIL",
    }
    write_json(out / "policy_impact_delta_report.json", policy_report)

    # Claim-resource map
    claim_map = {
        "ROB-C001": ["AgiBot World", "Open X-Embodiment", "RH20T", "LIBERO"],
        "ROB-C002": ["AgiBot World", "LIBERO"],
        "ROB-C003": ["Open X-Embodiment", "RH20T", "MuJoCo runtime"],
        "ROB-C004": ["RH20T", "MuJoCo runtime"],
        "ROB-C005": ["AgiBot World", "RH20T", "Open X-Embodiment"],
        "ROB-C006": ["Open X-Embodiment", "Octo policy comparator", "ROS2+MoveIt2 runtime"],
        "ROB-C007": ["RH20T"],
        "ROB-C008": ["Octo policy comparator", "Open X-Embodiment"],
    }
    write_json(
        out / "max_claim_resource_map.json",
        {
            "generated_at": dt.datetime.now(dt.UTC).isoformat(),
            "claim_map": claim_map,
            "evidence_artifacts": {
                "cross_embodiment": "cross_embodiment_consistency_report.json",
                "policy_impact": "policy_impact_delta_report.json",
                "validation_log": "max_resource_validation_log.md",
                "impracticality": "impracticality_decisions.json",
                "ros2_probe": "ros2_runtime_probe.json",
                "mujoco_probe": "mujoco_runtime_probe.json",
                "mujoco_parity": "mujoco_parity_report.json",
            },
        },
    )

    # Gap closure matrix
    imp_codes_by_resource = {item["resource"]: item["code"] for item in impractical}
    agibot_has_open_alt = agibot_metrics["numeric_samples"] > 0
    d2_le_lib_resolved = bool(lerobot_metrics["numeric_samples"] > 0 and libero_metrics["numeric_samples"] > 0)
    d2_ros_resolved = ros_probe["status"] == "PASS"
    d2_mujoco_resolved = mujoco_probe["status"] == "PASS"
    e3_openx_resolved = bool(openx_metrics["samples"] > 0)
    e3_rh20t_resolved = bool(rh20t_metrics["numeric_samples"] > 0)
    e3_octo_resolved = octo_probe["status"] == "PASS"

    gap_matrix = {
        "generated_at": dt.datetime.now(dt.UTC).isoformat(),
        "gaps": [
            {
                "gap_id": "D2-LE_ROBOT_LIBERO_DIRECT",
                "attempted": True,
                "status": _final_gap_status(d2_le_lib_resolved, imp_codes_by_resource.get("LeRobot"), True),
                "evidence": "max_resource_validation_log.md",
            },
            {
                "gap_id": "D2-ROS2_MOVEIT_NATIVE",
                "attempted": True,
                "status": _final_gap_status(
                    d2_ros_resolved,
                    imp_codes_by_resource.get("ROS2+MoveIt2 native runtime"),
                    True,
                ),
                "evidence": "ros2_runtime_probe.json",
                "imp_code": imp_codes_by_resource.get("ROS2+MoveIt2 native runtime"),
            },
            {
                "gap_id": "D2-MUJOCO_PARITY",
                "attempted": True,
                "status": _final_gap_status(
                    d2_mujoco_resolved,
                    imp_codes_by_resource.get("MuJoCo parity runtime"),
                    True,
                ),
                "evidence": "mujoco_parity_report.json",
                "imp_code": imp_codes_by_resource.get("MuJoCo parity runtime"),
            },
            {
                "gap_id": "E3-AGIBOT",
                "attempted": True,
                "status": _final_gap_status(
                    agibot_metrics["numeric_samples"] > 0,
                    imp_codes_by_resource.get("AgiBot World"),
                    agibot_has_open_alt,
                ),
                "evidence": "cross_embodiment_consistency_report.json",
                "imp_code": imp_codes_by_resource.get("AgiBot World"),
            },
            {
                "gap_id": "E3-OPENX",
                "attempted": True,
                "status": _final_gap_status(
                    e3_openx_resolved,
                    imp_codes_by_resource.get("Open X-Embodiment"),
                    True,
                ),
                "evidence": "max_resource_validation_log.md",
                "imp_code": imp_codes_by_resource.get("Open X-Embodiment"),
            },
            {
                "gap_id": "E3-RH20T",
                "attempted": True,
                "status": _final_gap_status(e3_rh20t_resolved, imp_codes_by_resource.get("RH20T"), True),
                "evidence": "cross_embodiment_consistency_report.json",
                "imp_code": imp_codes_by_resource.get("RH20T"),
            },
            {
                "gap_id": "E3-OCTO",
                "attempted": True,
                "status": _final_gap_status(
                    e3_octo_resolved,
                    imp_codes_by_resource.get("Octo policy comparator"),
                    True,
                ),
                "evidence": "policy_impact_delta_report.json",
                "imp_code": imp_codes_by_resource.get("Octo policy comparator"),
            },
        ],
    }
    write_json(out / "net_new_gap_closure_matrix.json", gap_matrix)

    attempted_e3 = {"AgiBot World": True, "Open X-Embodiment": True, "RH20T": True, "Octo policy comparator": True}
    e_g1 = all(attempted_e3.values())
    e_g2 = bool(cross_embodiment["multi_embodiment_evidence"])
    e_g3 = bool(octo_probe["status"] == "PASS" and policy_report["proxy_dataset_samples"] > 0)
    e_g4 = all(rec["code"] in ALLOWED_IMP_CODES for rec in impractical)
    requires_runpod = any(rec["code"] == "IMP-COMPUTE" for rec in impractical)

    # RunPod artifacts (required for IMP-COMPUTE)
    expected_artifacts = [
        "max_resource_lock.json",
        "max_resource_validation_log.md",
        "max_claim_resource_map.json",
        "impracticality_decisions.json",
        "cross_embodiment_consistency_report.json",
        "policy_impact_delta_report.json",
        "net_new_gap_closure_matrix.json",
        "ros2_runtime_probe.json",
        "mujoco_runtime_probe.json",
        "mujoco_parity_report.json",
    ]
    write_json(out / "runpod_expected_artifacts_manifest.json", {"artifacts": expected_artifacts})
    write_text(out / "runpod_requirements_lock.txt", _build_runpod_lock(sys.executable))

    if requires_runpod:
        runpod_commands = [
            "python3.11 -m venv .venv && source .venv/bin/activate",
            "python -m pip install --upgrade pip setuptools wheel",
            "python -m pip install -r runpod_requirements_lock.txt",
            "export HF_TOKEN=<token_with_agibot_access>",
            "python scripts/net_new_ingest.py --output-root proofs/reruns/robotics_wave1_local --seed 20260220 --sample-size 512",
            "python scripts/run_wave1.py --output-root proofs/reruns/robotics_wave1_local --seed 20260220 --determinism-runs 5 --max-wave",
            "python scripts/validate_net_new.py --artifacts proofs/reruns/robotics_wave1_local",
        ]
        runpod_manifest = {
            "generated_at": dt.datetime.now(dt.UTC).isoformat(),
            "status": "READY_FOR_DEFERRED_EXECUTION",
            "deferred_items": [rec for rec in impractical if rec["code"] == "IMP-COMPUTE"],
            "recommended_runtime": {
                "gpu": "NVIDIA RTX 4090 or A100 80GB",
                "cpu": "16 vCPU",
                "ram_gb": 64,
                "disk_gb": 500,
                "python": "3.11",
            },
            "pinned_dependencies_file": "runpod_requirements_lock.txt",
            "expected_artifact_manifest": "runpod_expected_artifacts_manifest.json",
            "exact_command_chain": runpod_commands,
            "artifacts_expected": expected_artifacts,
        }
        write_json(out / "runpod_readiness_manifest.json", runpod_manifest)
        runpod_plan = "\n".join(
            [
                "# RunPod Exec Plan",
                "",
                "Exact command chain:",
            ]
            + [f"{idx}. `{cmd}`" for idx, cmd in enumerate(runpod_commands, start=1)]
            + [
                "",
                "Validation focus:",
                "1. Resolve E3-OCTO direct comparator.",
                "2. Recompute M-gates and E-gates with updated evidence.",
                "3. Regenerate handoff artifacts and manifest checksums.",
                "",
            ]
        )
        write_text(out / "runpod_exec_plan.md", runpod_plan)
    else:
        write_json(
            out / "runpod_readiness_manifest.json",
            {"generated_at": dt.datetime.now(dt.UTC).isoformat(), "status": "NOT_REQUIRED", "reason": "no IMP-COMPUTE records"},
        )
        write_text(out / "runpod_exec_plan.md", "# RunPod Exec Plan\n\nNot required for this run.\n")

    e_g5 = all((out / name).exists() for name in RUNPOD_DEFERMENT_ARTIFACTS) if requires_runpod else True

    write_json(out / "max_resource_lock.json", resource_lock)
    write_json(out / "impracticality_decisions.json", {"records": impractical})
    write_text(out / "max_resource_validation_log.md", "\n".join(validation_lines) + "\n")

    m1_status = next(g["status"] for g in gap_matrix["gaps"] if g["gap_id"] == "D2-ROS2_MOVEIT_NATIVE")
    m2_status = next(g["status"] for g in gap_matrix["gaps"] if g["gap_id"] == "D2-LE_ROBOT_LIBERO_DIRECT")
    m3_status = next(g["status"] for g in gap_matrix["gaps"] if g["gap_id"] == "D2-MUJOCO_PARITY")
    m4_status = "PASS" if (policy_report["proxy_dataset_samples"] > 0 and policy_report["proxy_delta"] >= 0.0) else "FAIL"

    print(
        json.dumps(
            {
                "resource_attempts": {
                    "agibot_samples": agibot_metrics["samples"],
                    "openx_samples": openx_metrics["samples"],
                    "rh20t_samples": rh20t_metrics["samples"],
                },
                "m_gates": {"M1": m1_status, "M2": m2_status, "M3": m3_status, "M4": m4_status},
                "e_gates": {
                    "E-G1": "PASS" if e_g1 else "FAIL",
                    "E-G2": "PASS" if e_g2 else "FAIL",
                    "E-G3": "PASS" if e_g3 else "FAIL",
                    "E-G4": "PASS" if e_g4 else "FAIL",
                    "E-G5": "PASS" if e_g5 else "FAIL",
                },
                "impracticality_count": len(impractical),
                "requires_runpod": requires_runpod,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
