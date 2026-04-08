#!/usr/bin/env python3
"""Compress a fixture or LeRobot-derived episode directory into `.zpbot` packets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile
from typing import Any

import numpy as np

from zpe_robotics.enterprise_dataset import load_episode_matrices
from zpe_robotics.lerobot_codec import ZPELeRobotCodec, build_synthetic_episode, dump_episode_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compress a fixture or LeRobot-derived episode directory.")
    parser.add_argument("--dataset-root", type=Path, help="Optional bounded LeRobot dataset root acquired via scripts/acquire_enterprise_dataset.py.")
    parser.add_argument("--repo-id", default="lerobot/columbia_cairlab_pusht_real")
    parser.add_argument("--output-dir", type=Path, default=Path("example_output/lerobot"))
    return parser.parse_args()


def _write_fixture_dataset(dataset_dir: Path) -> dict[str, Any]:
    episode = build_synthetic_episode(frames=512, joints=8, hz=10.0)
    dump_episode_json(dataset_dir / "episode_000.json", episode)
    return {
        "mode": "fixture",
        "episode_metadata": episode["episode_metadata"],
        "joint_count": int(np.asarray(episode["joint_positions"]).shape[1]),
        "frame_count": int(np.asarray(episode["joint_positions"]).shape[0]),
    }


def _write_dataset_sample(dataset_root: Path, dataset_dir: Path, repo_id: str) -> dict[str, Any]:
    episodes, meta = load_episode_matrices(dataset_root, repo_id=repo_id, min_joints=6)
    if not episodes:
        raise ValueError(f"dataset {repo_id} yielded no usable episodes")

    episode = np.asarray(episodes[0], dtype=np.float32)
    fps = float(meta.get("fps") or 1.0)
    payload = {
        "joint_positions": episode,
        "timestamps": (np.arange(episode.shape[0], dtype=np.float64) / fps),
        "episode_metadata": {
            "repo_id": repo_id,
            "selected_field": str(meta.get("selected_field") or ""),
            "source_root": str(dataset_root),
            "fps": fps,
        },
    }
    dump_episode_json(dataset_dir / "episode_000.json", payload)
    return {
        "mode": "bounded_real_dataset",
        "episode_metadata": payload["episode_metadata"],
        "joint_count": int(episode.shape[1]),
        "frame_count": int(episode.shape[0]),
    }


def main() -> int:
    args = parse_args()
    codec = ZPELeRobotCodec()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="zpe_lerobot_example_") as temp_dir:
        dataset_dir = Path(temp_dir) / "dataset"
        dataset_dir.mkdir(parents=True, exist_ok=True)
        if args.dataset_root is None:
            source = _write_fixture_dataset(dataset_dir)
        else:
            source = _write_dataset_sample(args.dataset_root.resolve(), dataset_dir, str(args.repo_id))

        report = codec.compress_directory(dataset_dir, output_dir)
        packet_paths = sorted(output_dir.rglob("*.zpbot"))
        packet_path = packet_paths[0]
        decoded = codec.decode_episode(packet_path)
        replay = np.asarray(decoded["joint_positions"], dtype=np.float32)
        source_episode = json.loads((dataset_dir / "episode_000.json").read_text(encoding="utf-8"))
        original = np.asarray(source_episode["joint_positions"], dtype=np.float32)

    payload = {
        **source,
        "compression_ratio": float(report["compression_ratio"]),
        "files_processed": int(report["files_processed"]),
        "packet_count": len(packet_paths),
        "max_abs_error": float(np.max(np.abs(original - replay))),
        "output_dir": str(output_dir),
        "first_packet": str(packet_path),
    }
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
