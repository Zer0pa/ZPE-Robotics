"""Acquire a candidate enterprise benchmark dataset for Phase 9."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

from zpe_robotics.enterprise_dataset import qualify_dataset


CANDIDATES = [
    "lerobot/pusht",
    "lerobot/aloha_sim_insertion_scripted",
    "lerobot/aloha_sim_transfer_cube_scripted",
    "lerobot/xarm_lift_medium",
    "lerobot/columbia_cairlab_pusht_real",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Acquire a Phase 9 enterprise benchmark dataset.")
    parser.add_argument("--data-root", type=Path, default=Path("/workspace/data"))
    parser.add_argument("--output", type=Path, default=Path("/workspace/dataset_provenance.json"))
    parser.add_argument("--min-joints", type=int, default=6)
    parser.add_argument("--require-real", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    provenance: dict[str, object] = {"attempts": [], "selected": None, "timestamp": time.time()}

    try:
        from huggingface_hub import snapshot_download
    except Exception as exc:
        provenance["attempts"].append({"repo_id": "IMPORT", "status": f"FAILED: {exc}"})
        provenance["selected"] = {
            "repo_id": "SYNTHETIC",
            "path": "SYNTHETIC",
            "note": "huggingface_hub unavailable; falling back to synthetic 1000-frame 6-DOF fixture",
        }
        args.output.write_text(json.dumps(provenance, indent=2), encoding="utf-8")
        return 0

    for repo_id in CANDIDATES:
        try:
            local_dir = args.data_root / repo_id.split("/")[-1]
            snapshot_download(
                repo_id=repo_id,
                repo_type="dataset",
                local_dir=str(local_dir),
                ignore_patterns=["*.mp4", "*.png", "*.jpg", "*.jpeg"],
            )
            qualification = qualify_dataset(
                local_dir,
                repo_id=repo_id,
                min_joints=args.min_joints,
                require_real=args.require_real,
            )
            attempt_payload = {
                "repo_id": repo_id,
                "status": qualification.reason if not qualification.qualifies else "SUCCESS",
                "path": str(local_dir),
                "parquet_count": qualification.parquet_count,
                "selected_field": qualification.selected_field,
                "joint_count": qualification.joint_count,
                "fps": qualification.fps,
                "is_real_dataset": qualification.is_real,
                "total_episodes": qualification.total_episodes,
                "total_frames": qualification.total_frames,
            }
            provenance["attempts"].append(attempt_payload)
            if qualification.qualifies:
                provenance["selected"] = {
                    "repo_id": repo_id,
                    "path": str(local_dir),
                    "parquet_count": qualification.parquet_count,
                    "selected_field": qualification.selected_field,
                    "joint_count": qualification.joint_count,
                    "fps": qualification.fps,
                    "is_real_dataset": qualification.is_real,
                    "total_episodes": qualification.total_episodes,
                    "total_frames": qualification.total_frames,
                }
                break
        except Exception as exc:
            provenance["attempts"].append({"repo_id": repo_id, "status": f"FAILED: {exc}"})

    if not provenance["selected"]:
        provenance["selected"] = {
            "repo_id": "SYNTHETIC",
            "path": "SYNTHETIC",
            "note": "no qualifying dataset matched the requested benchmark constraints; falling back to synthetic 1000-frame 6-DOF fixture",
        }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
