#!/usr/bin/env python3
"""Hosted ARM64 parity probe with decisive artifact output."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import platform
import subprocess
import sys
import traceback
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

AUTHORITY_SURFACE = "zpbot-v2"
AUTHORITY_WIRE_COMPATIBILITY = "wire-v1"


REFERENCE_SHA256 = "a0941be23dc19bf96d7ec2e25f7ede9c051c3b28f51f141b89fdfc2691c3e125"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run ARM64 codec parity probe and emit decisive evidence")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "proofs" / "reruns" / f"arm64_parity_probe_{dt.date.today().isoformat()}" / "arm64_parity_result.json",
    )
    parser.add_argument(
        "--workflow-run-id",
        default=os.environ.get("GITHUB_RUN_ID", "local-dry-run"),
    )
    parser.add_argument(
        "--reference-sha256",
        default=REFERENCE_SHA256,
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = _base_payload(args)
    attempts: list[dict[str, Any]] = []

    try:
        _run_checked(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip", "uv"],
            attempts,
            timeout=1800,
        )
        _run_checked(["uv", "sync", "--dev", "--extra", "dev"], attempts, timeout=1800)
        _run_checked(["uv", "run", "pytest", "tests/test_codec.py", "tests/test_mcap_bridge.py", "-q"], attempts, timeout=1800)

        roundtrip_sha256, replay_sha256, bit_consistent = _compute_roundtrip(attempts)
        payload.update(
            {
                "status": "PASS"
                if bit_consistent and roundtrip_sha256 == args.reference_sha256
                else "FAIL",
                "roundtrip_sha256": roundtrip_sha256,
                "replay_sha256": replay_sha256,
                "x86_reference_sha256": args.reference_sha256,
                "hashes_match": bool(roundtrip_sha256 and roundtrip_sha256 == args.reference_sha256),
                "bit_consistent": bit_consistent,
                "attempt_log": attempts,
            }
        )
    except Exception as exc:  # pragma: no cover - defensive artifact guarantee
        payload.update(
            {
                "status": "FAIL",
                "roundtrip_sha256": "",
                "replay_sha256": "",
                "x86_reference_sha256": args.reference_sha256,
                "hashes_match": False,
                "bit_consistent": False,
                "attempt_log": attempts,
                "error": f"{type(exc).__name__}: {exc}",
                "traceback": traceback.format_exc(),
            }
        )

    _write_json(args.output, payload)
    return 0 if payload["status"] == "PASS" else 1


def _compute_roundtrip(attempts: list[dict[str, Any]]) -> tuple[str, str, bool]:
    probe_code = "\n".join(
        [
            "import json",
            "from zpe_robotics.codec import ZPBotCodec",
            "from zpe_robotics.fixtures import generate_joint_trajectory, make_rosbag_fixture",
            "from zpe_robotics.mcap_bridge import evaluate_bridge_roundtrip",
            "trajectory = generate_joint_trajectory(num_frames=4096, num_joints=6, seed=20260317)",
            "records = make_rosbag_fixture(trajectory, seed=20260318)",
            "result = evaluate_bridge_roundtrip(records, ZPBotCodec(keep_coeffs=8))",
            "print(json.dumps({",
            "    'original_sha256': result.original_sha256,",
            "    'replay_sha256': result.replay_sha256,",
            "    'bit_consistent': result.bit_consistent,",
            "}))",
        ]
    )
    proc = _run_checked(["uv", "run", "python", "-c", probe_code], attempts, timeout=1800)
    report = _parse_last_json_line(proc.stdout)
    return (
        str(report.get("original_sha256", "")),
        str(report.get("replay_sha256", "")),
        bool(report.get("bit_consistent", False)),
    )


def _run_checked(
    command: list[str],
    attempts: list[dict[str, Any]],
    *,
    timeout: int,
) -> subprocess.CompletedProcess[str]:
    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=timeout, cwd=ROOT)
    except FileNotFoundError as exc:
        attempts.append(
            {
                "command": " ".join(command),
                "returncode": 127,
                "stdout": "",
                "stderr": f"{type(exc).__name__}: {exc}",
            }
        )
        raise RuntimeError(f"command not found: {' '.join(command)}") from exc
    except subprocess.TimeoutExpired as exc:
        attempts.append(
            {
                "command": " ".join(command),
                "returncode": 124,
                "stdout": _coerce_text(exc.stdout),
                "stderr": _coerce_text(exc.stderr) or "timeout",
            }
        )
        raise RuntimeError(f"command timed out: {' '.join(command)}") from exc

    attempts.append(
        {
            "command": " ".join(command),
            "returncode": proc.returncode,
            "stdout": (proc.stdout or "").strip(),
            "stderr": (proc.stderr or "").strip(),
        }
    )
    if proc.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(command)}")
    return proc


def _parse_last_json_line(stdout: str) -> dict[str, Any]:
    lines = [line.strip() for line in stdout.splitlines() if line.strip()]
    if not lines:
        raise RuntimeError("roundtrip probe produced no JSON output")
    return json.loads(lines[-1])


def _coerce_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace").strip()
    return value.strip()


def _base_payload(args: argparse.Namespace) -> dict[str, Any]:
    platform_name = platform.platform()
    return {
        "authority_surface": AUTHORITY_SURFACE,
        "compatibility_mode": AUTHORITY_WIRE_COMPATIBILITY,
        "generation_timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
        "host_platform": platform_name,
        "platform": platform_name,
        "workflow_run_id": str(args.workflow_run_id),
    }


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
