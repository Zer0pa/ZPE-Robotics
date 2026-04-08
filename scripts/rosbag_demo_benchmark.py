#!/usr/bin/env python3
"""Generate a deterministic rosbag2-style demo benchmark artifact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import lz4.frame
import numpy as np
import zstandard

from zpe_robotics.fixtures import generate_joint_trajectory, make_rosbag_fixture
from zpe_robotics.release_candidate import default_codec
from zpe_robotics.rosbag_adapter import ZPBAG_NATIVE_VERSION, encode_records


TRAJECTORY_SEED = 20260410
RECORD_SEED = 20260411


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a deterministic rosbag2-style demo benchmark.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("proofs/artifacts/benchmarks/rosbag_demo_benchmark.json"),
    )
    return parser.parse_args()


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    output_path = args.output if args.output.is_absolute() else (_repo_root() / args.output)
    codec = default_codec()
    trajectory = generate_joint_trajectory(num_frames=4096, num_joints=6, seed=TRAJECTORY_SEED)
    records = make_rosbag_fixture(trajectory, seed=RECORD_SEED)

    raw_matrix = np.concatenate([np.asarray(record["trajectory"], dtype=np.float32) for record in records], axis=0)
    raw_float32_bytes = raw_matrix.tobytes(order="C")

    legacy_bag = encode_records(records, codec)
    native_mcap = encode_records(records, codec, version=ZPBAG_NATIVE_VERSION)
    zpbot_packets = [codec.encode(np.asarray(record["trajectory"], dtype=np.float64)) for record in records]
    zpbot_packet_bytes = sum(len(packet) for packet in zpbot_packets)
    zstd_l19 = zstandard.ZstdCompressor(level=19).compress(raw_float32_bytes)
    lz4_default = lz4.frame.compress(raw_float32_bytes)

    payload = {
        "dataset": "deterministic_rosbag2_demo_fixture",
        "record_count": len(records),
        "raw_float32_bytes": len(raw_float32_bytes),
        "comparators": {
            "legacy_bag": {
                "bytes": len(legacy_bag),
                "compression_ratio": float(len(raw_float32_bytes) / max(1, len(legacy_bag))),
            },
            "native_mcap": {
                "bytes": len(native_mcap),
                "compression_ratio": float(len(raw_float32_bytes) / max(1, len(native_mcap))),
            },
            "zstd_l19": {
                "bytes": len(zstd_l19),
                "compression_ratio": float(len(raw_float32_bytes) / max(1, len(zstd_l19))),
            },
            "lz4_default": {
                "bytes": len(lz4_default),
                "compression_ratio": float(len(raw_float32_bytes) / max(1, len(lz4_default))),
            },
            "zpbot_packet_library": {
                "bytes": zpbot_packet_bytes,
                "compression_ratio": float(len(raw_float32_bytes) / max(1, zpbot_packet_bytes)),
            },
        },
        "note": "This is a deterministic rosbag2-style demo fixture, not a hosted ROS2 runtime capture.",
    }
    _write_json(output_path, payload)
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
