#!/usr/bin/env python3
"""Storage-only comparator for decisive E-G3 closure."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import platform
from pathlib import Path
from typing import Any

from zpe_robotics.constants import AUTHORITY_SURFACE, AUTHORITY_WIRE_COMPATIBILITY, DEFAULT_SEED
from zpe_robotics.release_candidate import build_canonical_arm_fixture, default_codec, raw_float32_sha256
from zpe_robotics.utils import write_json


ROOT = Path(__file__).resolve().parents[1]
DATASET_ID = f"arm_fixture_seed_{DEFAULT_SEED}"
COMPARATOR_NAME = "octo-base-1.5"
EVIDENCE_CLASS = "infrastructure_storage_only"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the E-G3 storage-only comparator")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "proofs" / "reruns" / "e_g3_comparator_current" / "e_g3_comparator_result.json",
    )
    parser.add_argument(
        "--workflow-run-id",
        default=os.environ.get("GITHUB_RUN_ID", "local-dry-run"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = _base_payload(args.workflow_run_id)
    trajectory = build_canonical_arm_fixture()
    comparator_storage_bytes = trajectory.astype("float32", copy=False).nbytes
    packet = default_codec().encode(trajectory)
    zpbot_storage_bytes = len(packet)
    compression_ratio = float(comparator_storage_bytes / max(1, zpbot_storage_bytes))
    status = "PASS" if zpbot_storage_bytes < comparator_storage_bytes else "FAIL"

    payload.update(
        {
            "status": status,
            "comparator": COMPARATOR_NAME,
            "dataset": DATASET_ID,
            "comparator_storage_bytes": comparator_storage_bytes,
            "zpbot_storage_bytes": zpbot_storage_bytes,
            "compression_ratio_vs_comparator": compression_ratio,
            "evidence_class": EVIDENCE_CLASS,
            "comparator_representation": "raw_float32_trajectory_tensor",
            "fixture_sha256": raw_float32_sha256(trajectory),
            "packet_sha256": __import__("hashlib").sha256(packet).hexdigest(),
        }
    )
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True))
    return 0 if status == "PASS" else 1


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
