#!/usr/bin/env python
"""Run the Phase-2 ROS2 plus MoveIt2 bridge probe."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from zpe_robotics.runtime_probe import write_ros2_probe_artifact


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the ROS2 plus MoveIt2 bridge probe")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "proofs" / "reruns" / "it02_native_bridge_current" / "ros2_bridge_probe.json",
    )
    parser.add_argument("--strict", action="store_true", help="exit non-zero if the probe status is FAIL")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = write_ros2_probe_artifact(args.output)
    print(f"status={payload['status']} runtime_path={payload['runtime_path']} output={args.output}")
    if args.strict and payload["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
