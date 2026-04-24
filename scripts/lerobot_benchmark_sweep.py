#!/usr/bin/env python3
"""Phase 10 RunPod-first LeRobot benchmark sweep.

This script expands the Phase 9 benchmark surface across multiple HuggingFace
LeRobot-style datasets while keeping the run truthful:

- Every attempted dataset is recorded in a manifest (successes and failures).
- Dataset acquisition is bounded (meta/info.json + a capped parquet subset).
- Resolved HuggingFace revision SHAs are recorded for reproducibility.
- Results are per-dataset `enterprise_benchmark.py` outputs plus an aggregate
  spread summary.

It does not claim closure of Phase 9 blockers (B3, attack_3, Robotics Rust
routing) or create a general anomaly-readiness claim. Attack_5 is governed by
the separate anomaly threshold artifacts.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time
from typing import Any

import acquire_enterprise_dataset
from zpe_robotics.benchmark_sweep import dataset_family
from zpe_robotics.enterprise_dataset import qualify_dataset


PRIORITY_DATASETS = [
    "lerobot/columbia_cairlab_pusht_real",
    "IPEC-COMMUNITY/droid_lerobot",
    "IPEC-COMMUNITY/language_table_lerobot",
    "IPEC-COMMUNITY/bridge_orig_lerobot",
    "IPEC-COMMUNITY/fractal20220817_data_lerobot",
    "lerobot/aloha_mobile_shrimp",
    "lerobot/umi_cup_in_the_wild",
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _manifest_payload(args: argparse.Namespace, attempts: list[dict[str, Any]]) -> dict[str, Any]:
    benchmarked = [
        attempt
        for attempt in attempts
        if str((attempt.get("benchmark") or {}).get("status") or "") == "SUCCESS"
    ]
    return {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "config": {
            "datasets": list(args.datasets),
            "min_joints": int(args.min_joints),
            "min_qualified": int(args.min_qualified),
            "min_families": int(args.min_families),
            "require_real": bool(args.require_real),
            "runs": int(args.runs),
            "target_frames": int(args.target_frames),
            "max_parquet_files": int(args.max_parquet_files),
            "max_total_bytes": int(args.max_total_bytes),
            "revision": str((args.revision or "").strip()),
            "prune_unplanned_parquets": not args.keep_unplanned_parquets,
        },
        "attempts": attempts,
        "attempt_count": len(attempts),
        "benchmarked_count": len(benchmarked),
    }


def _write_manifest_snapshot(output_dir: Path, args: argparse.Namespace, attempts: list[dict[str, Any]]) -> None:
    _write_json(output_dir / "dataset_manifest.json", _manifest_payload(args, attempts))


def _spread(values: list[float]) -> dict[str, float]:
    if not values:
        return {"min": float("nan"), "median": float("nan"), "max": float("nan")}
    return {"min": float(min(values)), "median": float(statistics.median(values)), "max": float(max(values))}


def _extract_zpe_tool_metrics(benchmark_payload: dict[str, Any]) -> dict[str, Any]:
    results = benchmark_payload.get("results") or {}
    zpe = results.get("zpe_p8") or {}
    dataset_meta = benchmark_payload.get("dataset_meta") or {}
    return {
        "compression_ratio": float(zpe.get("compression_ratio", float("nan"))),
        "encode_time_ms_p50": float(zpe.get("encode_time_ms_p50", float("nan"))),
        "decode_time_ms_p50": float(zpe.get("decode_time_ms_p50", float("nan"))),
        "bit_exact_replay": bool(zpe.get("bit_exact_replay", False)),
        "max_abs_error": float(zpe.get("max_abs_error", float("nan"))),
        "sample_shape": dataset_meta.get("sample_shape") or benchmark_payload.get("sample_shape") or [],
        "dataset_meta": {
            "repo_id": dataset_meta.get("repo_id", benchmark_payload.get("dataset_name", "")),
            "selected_field": dataset_meta.get("selected_field"),
            "joint_count": dataset_meta.get("joint_count"),
            "fps": dataset_meta.get("fps"),
            "episode_count_total": dataset_meta.get("episode_count_total"),
            "frame_count_total": dataset_meta.get("frame_count_total"),
            "declared_total_episodes": dataset_meta.get("declared_total_episodes"),
            "declared_total_frames": dataset_meta.get("declared_total_frames"),
            "is_real_dataset": dataset_meta.get("is_real_dataset"),
            "qualified_reason": dataset_meta.get("qualified_reason"),
            "dataset_root": dataset_meta.get("dataset_root"),
        },
    }


def _default_output_dir() -> Path:
    return _repo_root() / "proofs" / "artifacts" / "lerobot_expanded_benchmarks"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a bounded multi-dataset LeRobot benchmark sweep.")
    parser.add_argument("--data-root", type=Path, default=Path("/workspace/data_phase10"))
    parser.add_argument("--output-dir", type=Path, default=_default_output_dir())
    parser.add_argument("--datasets", nargs="*", default=list(PRIORITY_DATASETS))
    parser.add_argument("--min-joints", type=int, default=6)
    parser.add_argument("--min-qualified", type=int, default=3)
    parser.add_argument("--min-families", type=int, default=2)
    parser.add_argument("--require-real", action="store_true")
    parser.add_argument("--runs", type=int, default=50)
    parser.add_argument("--target-frames", type=int, default=1000)
    parser.add_argument("--max-parquet-files", type=int, default=acquire_enterprise_dataset.DEFAULT_MAX_PARQUET_FILES)
    parser.add_argument("--max-total-bytes", type=int, default=acquire_enterprise_dataset.DEFAULT_MAX_TOTAL_BYTES)
    parser.add_argument("--revision", type=str, default="")
    parser.add_argument("--keep-unplanned-parquets", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    revision = args.revision.strip() or None
    prune_unplanned = not args.keep_unplanned_parquets

    repo_root = _repo_root()
    enterprise_benchmark = repo_root / "scripts" / "enterprise_benchmark.py"
    output_dir = args.output_dir if args.output_dir.is_absolute() else (repo_root / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(
        output_dir / "dataset_index.json",
        {
            "priority_datasets": list(args.datasets),
            "selection_floor": {
                "min_qualified_datasets": int(args.min_qualified),
                "min_materially_distinct_families": int(args.min_families),
            },
            "substitution_policy": (
                "Attempt the full priority set. Preserve every acquisition or qualification miss in "
                "dataset_manifest.json. Do not substitute synthetic or sim-only datasets into the "
                "governing expanded-benchmark claim."
            ),
        },
    )

    attempts: list[dict[str, Any]] = []
    benchmark_summaries: list[dict[str, Any]] = []

    for repo_id in list(args.datasets):
        started = time.time()
        dataset_slug = acquire_enterprise_dataset._sanitize_repo_id(repo_id)  # noqa: SLF001
        local_dir = acquire_enterprise_dataset._choose_local_dir(  # noqa: SLF001
            data_root=args.data_root, repo_id=repo_id, include_namespace=True
        )
        dataset_out_dir = output_dir / dataset_slug
        dataset_out_dir.mkdir(parents=True, exist_ok=True)
        provenance_path = dataset_out_dir / "dataset_provenance.json"

        attempt: dict[str, Any] = {
            "repo_id": repo_id,
            "dataset_slug": dataset_slug,
            "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started)),
            "duration_seconds": 0.0,
            "download": {},
            "qualification": {},
            "benchmark": {},
        }
        try:
            download = acquire_enterprise_dataset._download_dataset_partial(  # noqa: SLF001
                repo_id,
                local_dir=local_dir,
                revision=revision,
                max_parquet_files=int(args.max_parquet_files),
                max_total_bytes=int(args.max_total_bytes),
                prune_unplanned=prune_unplanned,
            )
            attempt["download"] = download

            if download.get("status") != "SUCCESS":
                attempt["benchmark"] = {"status": "SKIPPED", "reason": "DOWNLOAD_FAILED"}
                continue

            qualification = qualify_dataset(
                Path(str(download.get("local_dir") or local_dir)),
                repo_id=repo_id,
                min_joints=int(args.min_joints),
                require_real=bool(args.require_real),
            )
            attempt["qualification"] = {
                "qualifies": bool(qualification.qualifies),
                "reason": qualification.reason,
                "selected_field": qualification.selected_field,
                "joint_count": qualification.joint_count,
                "fps": qualification.fps,
                "is_real_dataset": qualification.is_real,
                "parquet_count": qualification.parquet_count,
                "total_episodes": qualification.total_episodes,
                "total_frames": qualification.total_frames,
            }

            if not qualification.qualifies:
                attempt["benchmark"] = {"status": "SKIPPED", "reason": "NOT_QUALIFIED"}
                continue

            _write_json(provenance_path, attempt)

            cmd = [
                sys.executable,
                str(enterprise_benchmark),
                "--dataset-root",
                str(local_dir),
                "--dataset-name",
                repo_id,
                "--dataset-provenance",
                str(provenance_path),
                "--output-dir",
                str(dataset_out_dir),
                "--runs",
                str(int(args.runs)),
                "--target-frames",
                str(int(args.target_frames)),
                "--sample-mode",
                "episode_window",
            ]
            proc = subprocess.run(cmd, cwd=str(repo_root), text=True, capture_output=True, check=False)

            attempt["benchmark"] = {
                "status": "SUCCESS" if proc.returncode == 0 else "FAILED",
                "returncode": int(proc.returncode),
                "stdout_tail": (proc.stdout or "")[-4000:],
                "stderr_tail": (proc.stderr or "")[-4000:],
                "output_dir": str(dataset_out_dir),
            }

            benchmark_path = dataset_out_dir / "benchmark_result.json"
            if proc.returncode == 0 and benchmark_path.exists():
                payload = _read_json(benchmark_path)
                summary = _extract_zpe_tool_metrics(payload)
                summary["repo_id"] = repo_id
                summary["revision"] = str(download.get("revision") or "")
                summary["benchmark_result_path"] = str(benchmark_path)
                benchmark_summaries.append(summary)
        except Exception as exc:  # noqa: BLE001
            attempt["benchmark"] = {
                "status": "FAILED",
                "reason": "UNHANDLED_EXCEPTION",
                "error": f"{type(exc).__name__}: {exc}",
            }
        finally:
            attempt["duration_seconds"] = float(time.time() - started)
            attempts.append(attempt)
            _write_json(provenance_path, attempt)
            _write_manifest_snapshot(output_dir, args, attempts)

    standing: dict[str, Any] = {}
    gate_path = repo_root / "proofs" / "enterprise_benchmark" / "GATE_VERDICTS.json"
    if gate_path.exists():
        try:
            standing["phase9_gate_verdicts"] = _read_json(gate_path)
        except Exception:
            standing["phase9_gate_verdicts_error"] = f"failed to read {gate_path}"

    red_team_path = repo_root / "proofs" / "red_team" / "red_team_report.json"
    if red_team_path.exists():
        try:
            report = _read_json(red_team_path)
            verdicts: dict[str, str] = {}
            for attack in report.get("attacks", []):
                attack_id = str(attack.get("attack_id") or "")
                verdict = str(attack.get("verdict") or "")
                if attack_id:
                    verdicts[attack_id] = verdict
            standing["phase9_red_team_verdicts"] = verdicts
        except Exception:
            standing["phase9_red_team_verdicts_error"] = f"failed to read {red_team_path}"

    anchor: dict[str, Any] = {}
    anchor_metrics: dict[str, Any] = {}
    anchor_path = repo_root / "proofs" / "enterprise_benchmark" / "benchmark_result.json"
    if anchor_path.exists():
        try:
            anchor = _read_json(anchor_path)
            anchor_metrics = _extract_zpe_tool_metrics(anchor)
            anchor_metrics["benchmark_result_path"] = str(anchor_path)
        except Exception:
            anchor_metrics = {"error": f"failed to read {anchor_path}"}

    regressions: list[dict[str, Any]] = []
    if anchor_metrics and "error" not in anchor_metrics:
        anchor_ratio = float(anchor_metrics.get("compression_ratio", float("nan")))
        anchor_encode = float(anchor_metrics.get("encode_time_ms_p50", float("nan")))
        anchor_decode = float(anchor_metrics.get("decode_time_ms_p50", float("nan")))
        anchor_error = float(anchor_metrics.get("max_abs_error", float("nan")))

        for item in benchmark_summaries:
            repo_id = str(item.get("repo_id") or "")
            ratio = float(item.get("compression_ratio", float("nan")))
            encode = float(item.get("encode_time_ms_p50", float("nan")))
            decode = float(item.get("decode_time_ms_p50", float("nan")))
            max_err = float(item.get("max_abs_error", float("nan")))

            if ratio == ratio and anchor_ratio == anchor_ratio and ratio < anchor_ratio:
                regressions.append(
                    {
                        "repo_id": repo_id,
                        "metric": "compression_ratio",
                        "value": ratio,
                        "anchor": anchor_ratio,
                        "delta": float(ratio - anchor_ratio),
                    }
                )
            if encode == encode and anchor_encode == anchor_encode and encode > anchor_encode:
                regressions.append(
                    {
                        "repo_id": repo_id,
                        "metric": "encode_time_ms_p50",
                        "value": encode,
                        "anchor": anchor_encode,
                        "delta": float(encode - anchor_encode),
                    }
                )
            if decode == decode and anchor_decode == anchor_decode and decode > anchor_decode:
                regressions.append(
                    {
                        "repo_id": repo_id,
                        "metric": "decode_time_ms_p50",
                        "value": decode,
                        "anchor": anchor_decode,
                        "delta": float(decode - anchor_decode),
                    }
                )
            if max_err == max_err and anchor_error == anchor_error and max_err > anchor_error:
                regressions.append(
                    {
                        "repo_id": repo_id,
                        "metric": "max_abs_error",
                        "value": max_err,
                        "anchor": anchor_error,
                        "delta": float(max_err - anchor_error),
                    }
                )

    compression_values = [float(item.get("compression_ratio", float("nan"))) for item in benchmark_summaries]
    encode_values = [float(item.get("encode_time_ms_p50", float("nan"))) for item in benchmark_summaries]
    decode_values = [float(item.get("decode_time_ms_p50", float("nan"))) for item in benchmark_summaries]
    error_values = [float(item.get("max_abs_error", float("nan"))) for item in benchmark_summaries]
    benchmarked_families = sorted({dataset_family(str(item.get("repo_id") or "")) for item in benchmark_summaries if item.get("repo_id")})
    acceptance_pass = len(benchmark_summaries) >= int(args.min_qualified) and len(benchmarked_families) >= int(args.min_families)

    aggregate = {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": "PASS" if acceptance_pass else "FAIL",
        "requirements": {
            "min_qualified_datasets": int(args.min_qualified),
            "min_materially_distinct_families": int(args.min_families),
        },
        "benchmarked_dataset_count": len(benchmark_summaries),
        "materially_distinct_families": benchmarked_families,
        "results": benchmark_summaries,
        "standing_blockers": standing,
        "phase9_anchor": anchor_metrics,
        "regressions_vs_phase9_anchor": regressions,
        "spread": {
            "zpe_p8": {
                "compression_ratio": _spread([v for v in compression_values if v == v]),
                "encode_time_ms_p50": _spread([v for v in encode_values if v == v]),
                "decode_time_ms_p50": _spread([v for v in decode_values if v == v]),
                "max_abs_error": _spread([v for v in error_values if v == v]),
            }
        },
        "standing_blockers_note": (
            "Benchmark breadth is not blocker closure. B3 (bit-exact replay), red-team attack_3, and "
            "Robotics Rust routing remain unresolved unless separately proven by governing proof artifacts. "
            "attack_5 is governed by the anomaly threshold artifacts, not by benchmark breadth."
        ),
    }
    _write_json(output_dir / "aggregate_spread_summary.json", aggregate)
    return 0 if acceptance_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
