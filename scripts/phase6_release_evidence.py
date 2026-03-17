#!/usr/bin/env python3
"""Generate Phase 6 release-candidate evidence artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import tempfile
from pathlib import Path
from typing import Any

from zpe_robotics.anomaly import evaluate_anomaly_detector
from zpe_robotics.constants import AUTHORITY_SURFACE, AUTHORITY_WIRE_COMPATIBILITY
from zpe_robotics.lerobot_codec import evaluate_lerobot_roundtrip
from zpe_robotics.primitive_index import evaluate_primitive_search
from zpe_robotics.utils import write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Phase 6 release-candidate evidence artifacts.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("proofs/release_candidate"),
        help="Directory where release-candidate evidence JSON files will be written.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="zpe_phase6_evidence_") as tmp:
        tmp_root = Path(tmp)
        lerobot = _envelope(evaluate_lerobot_roundtrip(tmp_root / "lerobot"))
        write_json(output_dir / "lerobot_codec_result.json", lerobot)

        primitive = _envelope(evaluate_primitive_search(tmp_root / "primitive"))
        write_json(output_dir / "primitive_search_result.json", primitive)

        anomaly = _envelope(evaluate_anomaly_detector(tmp_root / "anomaly"))
        write_json(output_dir / "anomaly_detection_result.json", anomaly)

    return 0


def _envelope(payload: dict[str, Any]) -> dict[str, Any]:
    timestamp = dt.datetime.now(dt.timezone.utc).isoformat()
    return {
        "authority_surface": AUTHORITY_SURFACE,
        "compatibility_mode": AUTHORITY_WIRE_COMPATIBILITY,
        "generation_timestamp": timestamp,
        **payload,
    }


if __name__ == "__main__":
    raise SystemExit(main())
