#!/usr/bin/env python3
"""Run a deterministic bag -> `.zpbot` -> deterministic bag roundtrip example."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from zpe_robotics.release_candidate import build_canonical_arm_fixture, default_codec, encode_single_record_bag
from zpe_robotics.rosbag_adapter import decode_records
from zpe_robotics.utils import sha256_bytes


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Roundtrip a deterministic bag through `.zpbot`.")
    parser.add_argument("--output-dir", type=Path, default=Path("example_output/rosbag"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    codec = default_codec()
    trajectory = build_canonical_arm_fixture()
    input_blob = encode_single_record_bag(trajectory, codec)
    packet_blob = codec.encode(trajectory)
    replay_blob = encode_single_record_bag(codec.decode(packet_blob), codec)

    input_path = output_dir / "arm_fixture.bag"
    packet_path = output_dir / "arm_fixture.zpbot"
    replay_path = output_dir / "arm_fixture_replay.bag"
    input_path.write_bytes(input_blob)
    packet_path.write_bytes(packet_blob)
    replay_path.write_bytes(replay_blob)

    replay_records = decode_records(replay_blob, codec, decode_trajectory=True, strict_index=True)
    replay = np.asarray(replay_records[0]["trajectory"], dtype=np.float64)
    max_abs_error = float(np.max(np.abs(trajectory - replay)))

    payload = {
        "artifacts": {
            "input_bag": str(input_path),
            "packet": str(packet_path),
            "replay_bag": str(replay_path),
        },
        "array_close": bool(np.allclose(trajectory, replay, atol=0.3)),
        "bit_consistent": bool(input_blob == replay_blob),
        "compression_ratio": float((trajectory.astype(np.float32).nbytes) / max(1, len(packet_blob))),
        "input_sha256": sha256_bytes(input_blob),
        "packet_sha256": sha256_bytes(packet_blob),
        "replay_sha256": sha256_bytes(replay_blob),
        "max_abs_error": max_abs_error,
        "records": len(replay_records),
    }
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
