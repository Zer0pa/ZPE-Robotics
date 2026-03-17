#!/usr/bin/env python3
"""Per-lane parity probe for the IT-04 matrix workflow."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import platform
from pathlib import Path
from typing import Any

from zpe_robotics.constants import AUTHORITY_SURFACE, AUTHORITY_WIRE_COMPATIBILITY
from zpe_robotics.release_candidate import REFERENCE_ROUNDTRIP_SHA256, compute_reference_bridge_roundtrip, default_codec
from zpe_robotics.utils import write_json


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a single IT-04 parity lane")
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--workflow-run-id",
        default=os.environ.get("GITHUB_RUN_ID", "local-dry-run"),
    )
    parser.add_argument(
        "--platform-label",
        default="local",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = compute_reference_bridge_roundtrip(default_codec())
    status = "PASS"
    hashes_match = report["original_sha256"] == REFERENCE_ROUNDTRIP_SHA256 == report["replay_sha256"]
    if not hashes_match or not report["bit_consistent"]:
        status = "FAIL"

    payload = _base_payload(args.workflow_run_id, args.platform_label)
    payload.update(
        {
            "status": status,
            "roundtrip_sha256": report["original_sha256"],
            "replay_sha256": report["replay_sha256"],
            "x86_reference_sha256": REFERENCE_ROUNDTRIP_SHA256,
            "hashes_match": hashes_match,
            "bit_consistent": bool(report["bit_consistent"]),
            "records": report["records"],
        }
    )
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True))
    return 0 if status == "PASS" else 1


def _base_payload(workflow_run_id: str, platform_label: str) -> dict[str, Any]:
    timestamp = dt.datetime.now(dt.timezone.utc).isoformat()
    host_platform = platform.platform()
    return {
        "authority_surface": AUTHORITY_SURFACE,
        "compatibility_mode": AUTHORITY_WIRE_COMPATIBILITY,
        "generation_timestamp": timestamp,
        "timestamp": timestamp,
        "host_platform": host_platform,
        "platform": host_platform,
        "platform_label": platform_label,
        "workflow_run_id": str(workflow_run_id),
    }


if __name__ == "__main__":
    raise SystemExit(main())
