#!/usr/bin/env python3
"""IT-03 and IT-05 composition proof for the deterministic motion kernel."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import platform
from pathlib import Path
from typing import Any, Callable

from zpe_robotics.codec import joint_rmse_deg
from zpe_robotics.constants import AUTHORITY_SURFACE, AUTHORITY_WIRE_COMPATIBILITY
from zpe_robotics.release_candidate import (
    REFERENCE_ROUNDTRIP_SHA256,
    build_single_packet_composition,
    compute_reference_bridge_roundtrip,
    decode_single_packet_bag,
    default_codec,
)
from zpe_robotics.utils import sha256_bytes, write_json
from zpe_robotics.wire import HEADER_SIZE, WireFormatError, decode_packet, describe_packet


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the IT-03 and IT-05 composition proof")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "proofs" / "reruns" / "it03_it05_composition_2026-03-17" / "it03_it05_composition_result.json",
    )
    parser.add_argument(
        "--workflow-run-id",
        default=os.environ.get("GITHUB_RUN_ID", "local-dry-run"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    codec = default_codec()
    composition = build_single_packet_composition(codec)
    decoded = decode_single_packet_bag(composition.bag_blob, codec)
    rmse_deg = joint_rmse_deg(composition.trajectory, decoded)
    reference_report = compute_reference_bridge_roundtrip(codec)
    hostile_paths = _hostile_path_results(composition.packet)

    steps = {
        "encode_packet": {
            "status": "PASS",
            "packet_sha256": sha256_bytes(composition.packet),
            "packet_bytes": len(composition.packet),
            "packet_info": describe_packet(composition.packet),
        },
        "wrap_zpbag1": {
            "status": "PASS",
            "bag_sha256": sha256_bytes(composition.bag_blob),
            "bag_bytes": len(composition.bag_blob),
            "records": 1,
        },
        "decode_packet": {
            "status": "PASS" if rmse_deg <= 0.05 else "FAIL",
            "trajectory_rmse_deg": rmse_deg,
            "trajectory_shape": list(decoded.shape),
        },
        "reference_hash_check": {
            "status": "PASS"
            if reference_report["original_sha256"] == REFERENCE_ROUNDTRIP_SHA256
            and reference_report["replay_sha256"] == REFERENCE_ROUNDTRIP_SHA256
            else "FAIL",
            "roundtrip_sha256": reference_report["original_sha256"],
            "replay_sha256": reference_report["replay_sha256"],
            "x86_reference_sha256": REFERENCE_ROUNDTRIP_SHA256,
            "hashes_match": bool(reference_report["original_sha256"] == REFERENCE_ROUNDTRIP_SHA256),
            "bit_consistent": bool(reference_report["bit_consistent"]),
        },
    }

    overall_pass = all(step["status"] == "PASS" for step in steps.values()) and all(
        path["status"] == "PASS" for path in hostile_paths
    )
    payload = _base_payload(args.workflow_run_id)
    payload.update(
        {
            "status": "PASS" if overall_pass else "FAIL",
            "steps": steps,
            "hostile_paths": hostile_paths,
            "attempt_log": _attempt_log(steps, hostile_paths),
        }
    )
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True))
    return 0 if overall_pass else 1


def _hostile_path_results(packet: bytes) -> list[dict[str, Any]]:
    return [
        _expected_failure(
            "corrupt_magic_bytes",
            b"BAD!!" + packet[5:],
            "invalid packet magic",
            decode_packet,
        ),
        _expected_failure(
            "crc32_mismatch",
            _mutate_last_byte(packet),
            "payload CRC mismatch",
            decode_packet,
        ),
        _expected_failure(
            "truncated_payload",
            packet[: max(HEADER_SIZE, len(packet) - 11)],
            "payload CRC mismatch",
            decode_packet,
        ),
    ]


def _expected_failure(
    name: str,
    payload: bytes,
    expected_error: str,
    decode_fn: Callable[[bytes], Any],
) -> dict[str, Any]:
    actual_error = ""
    outcome = "PASS"
    try:
        decode_fn(payload)
        outcome = "FAIL"
        actual_error = "decode unexpectedly succeeded"
    except Exception as exc:  # noqa: BLE001 - preserve exact failure surface
        actual_error = str(exc)
        if expected_error not in actual_error:
            outcome = "FAIL"
    return {
        "name": name,
        "expected_outcome": "FAIL",
        "status": outcome,
        "expected_error_contains": expected_error,
        "actual_error": actual_error,
    }


def _mutate_last_byte(packet: bytes) -> bytes:
    tampered = bytearray(packet)
    tampered[-1] ^= 0x7F
    return bytes(tampered)


def _attempt_log(steps: dict[str, dict[str, Any]], hostile_paths: list[dict[str, Any]]) -> list[dict[str, Any]]:
    log = []
    for name, payload in steps.items():
        log.append({"step": name, "status": payload["status"]})
    for payload in hostile_paths:
        log.append(
            {
                "step": payload["name"],
                "status": payload["status"],
                "expected_outcome": payload["expected_outcome"],
                "actual_error": payload["actual_error"],
            }
        )
    return log


def _base_payload(workflow_run_id: str) -> dict[str, Any]:
    timestamp = dt.datetime.now(dt.timezone.utc).isoformat()
    host_platform = platform.platform()
    return {
        "authority_surface": AUTHORITY_SURFACE,
        "compatibility_mode": AUTHORITY_WIRE_COMPATIBILITY,
        "generation_timestamp": timestamp,
        "timestamp": timestamp,
        "host_platform": host_platform,
        "platform": host_platform,
        "workflow_run_id": str(workflow_run_id),
    }


if __name__ == "__main__":
    raise SystemExit(main())
