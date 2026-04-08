#!/usr/bin/env python3
"""Create a native MCAP-backed bag example and query its metadata without decoding trajectories."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from zpe_robotics.fixtures import generate_joint_trajectory, make_rosbag_fixture
from zpe_robotics.release_candidate import default_codec
from zpe_robotics.rosbag_adapter import (
    ZPBAG_NATIVE_VERSION,
    bag_info,
    encode_records,
    evaluate_roundtrip,
    read_mcap_native_index,
)
from zpe_robotics.utils import sha256_bytes


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a native MCAP-backed bridge example.")
    parser.add_argument("--output-dir", type=Path, default=Path("example_output/mcap"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    codec = default_codec()
    trajectory = generate_joint_trajectory(num_frames=4096, num_joints=6, seed=20260408)
    records = make_rosbag_fixture(trajectory, seed=20260409)
    raw_bytes = sum(np.asarray(record["trajectory"], dtype=np.float32).nbytes for record in records)
    blob = encode_records(records, codec, version=ZPBAG_NATIVE_VERSION)
    path = output_dir / "arm_fixture.mcap"
    path.write_bytes(blob)

    index = read_mcap_native_index(path)
    info = bag_info(blob, codec)
    roundtrip = evaluate_roundtrip(records, codec, version=ZPBAG_NATIVE_VERSION)
    query_topic = "/joint_states"
    query_hits = [record for record in index["records"] if record["topic"] == query_topic]

    payload = {
        "artifacts": {
            "native_mcap": str(path),
        },
        "bit_consistent": bool(roundtrip.bit_consistent),
        "compression_ratio": float(raw_bytes / max(1, len(blob))),
        "native_mcap_sha256": sha256_bytes(blob),
        "records": len(index["records"]),
        "search_without_decode": {
            "query_topic": query_topic,
            "hits": len(query_hits),
            "index_version": index["version"],
        },
        "summary": info,
    }
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
