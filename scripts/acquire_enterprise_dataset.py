"""Acquire candidate LeRobot datasets for benchmarking.

Phase 9 used a single qualifying dataset. Phase 10 expands the benchmark
surface across multiple datasets, which requires a bounded acquisition strategy
so RunPod does not clone entire HuggingFace datasets by accident.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
import time
from typing import Any

from zpe_robotics.enterprise_dataset import qualify_dataset


CANDIDATES = [
    "lerobot/pusht",
    "lerobot/aloha_sim_insertion_scripted",
    "lerobot/aloha_sim_transfer_cube_scripted",
    "lerobot/xarm_lift_medium",
    "lerobot/columbia_cairlab_pusht_real",
]

DEFAULT_MAX_PARQUET_FILES = 4
DEFAULT_MAX_TOTAL_BYTES = 800_000_000


def _sanitize_repo_id(repo_id: str) -> str:
    """Create a filesystem-safe slug from a HuggingFace repo_id."""

    cleaned = repo_id.strip()
    cleaned = re.sub(r"[^a-zA-Z0-9._/-]+", "_", cleaned)
    cleaned = cleaned.replace("/", "__")
    return cleaned or "unknown_dataset"


def _choose_local_dir(*, data_root: Path, repo_id: str, include_namespace: bool) -> Path:
    if include_namespace:
        return data_root / _sanitize_repo_id(repo_id)
    return data_root / repo_id.split("/")[-1]


def _select_partial_download_files(
    repo_files: list[dict[str, Any]],
    *,
    max_parquet_files: int,
    max_total_bytes: int,
) -> dict[str, Any]:
    """Return a download plan dict from a HuggingFace repo file listing.

    The plan always includes `meta/info.json` when present, and then selects a
    bounded number of parquet shards under a total byte cap.
    """

    info_files = [item for item in repo_files if item.get("path") == "meta/info.json"]
    parquet_files = [
        item
        for item in repo_files
        if str(item.get("path", "")).startswith("data/") and str(item.get("path", "")).endswith(".parquet")
    ]

    parquet_files_sorted = sorted(
        parquet_files,
        key=lambda item: (int(item.get("size") or 0), str(item.get("path") or "")),
    )

    planned: list[dict[str, Any]] = []
    total_bytes = 0

    for item in info_files:
        planned.append(item)
        total_bytes += int(item.get("size") or 0)

    parquet_selected: list[dict[str, Any]] = []
    for item in parquet_files_sorted:
        if len(parquet_selected) >= max_parquet_files:
            break
        size = int(item.get("size") or 0)
        if (total_bytes + size) > max_total_bytes:
            continue
        parquet_selected.append(item)
        total_bytes += size

    planned.extend(parquet_selected)

    return {
        "planned_files": planned,
        "planned_file_count": len(planned),
        "planned_total_bytes": total_bytes,
        "planned_parquet_count": len(parquet_selected),
        "max_parquet_files": max_parquet_files,
        "max_total_bytes": max_total_bytes,
    }


def _prune_unplanned_parquets(local_dir: Path, planned_paths: set[str]) -> list[str]:
    removed: list[str] = []
    data_root = local_dir / "data"
    if not data_root.exists():
        return removed
    for parquet_path in data_root.rglob("*.parquet"):
        try:
            rel = parquet_path.relative_to(local_dir).as_posix()
        except Exception:
            continue
        if rel in planned_paths:
            continue
        try:
            parquet_path.unlink()
        except OSError:
            continue
        removed.append(rel)
    return sorted(removed)


def _download_dataset_partial(
    repo_id: str,
    *,
    local_dir: Path,
    revision: str | None,
    max_parquet_files: int,
    max_total_bytes: int,
    prune_unplanned: bool,
) -> dict[str, Any]:
    """Download a bounded subset of dataset files to `local_dir`."""

    try:
        from huggingface_hub import HfApi, hf_hub_download  # type: ignore
    except Exception as exc:  # noqa: BLE001
        return {"status": "FAILED", "error": f"huggingface_hub unavailable: {exc}"}

    api = HfApi()
    try:
        info = api.dataset_info(repo_id, revision=revision)
    except Exception as exc:  # noqa: BLE001
        return {"status": "FAILED", "error": f"dataset_info failed: {type(exc).__name__}: {exc}"}

    resolved_revision = str(getattr(info, "sha", "") or revision or "")
    if not resolved_revision:
        return {"status": "FAILED", "error": "could not resolve dataset revision sha"}

    try:
        tree = api.list_repo_tree(repo_id, repo_type="dataset", revision=resolved_revision, recursive=True)
    except Exception as exc:  # noqa: BLE001
        return {"status": "FAILED", "error": f"list_repo_tree failed: {type(exc).__name__}: {exc}", "revision": resolved_revision}

    repo_files: list[dict[str, Any]] = []
    for item in tree:
        path = getattr(item, "path", None)
        size = getattr(item, "size", None)
        if path in (None, ""):
            continue
        if not isinstance(size, (int, float)):
            continue
        repo_files.append({"path": str(path), "size": int(size)})

    plan = _select_partial_download_files(
        repo_files,
        max_parquet_files=max_parquet_files,
        max_total_bytes=max_total_bytes,
    )
    planned_files = list(plan["planned_files"])
    planned_paths = {str(item.get("path")) for item in planned_files if item.get("path")}

    local_dir.mkdir(parents=True, exist_ok=True)
    downloaded: list[dict[str, Any]] = []
    for item in planned_files:
        path = str(item.get("path") or "")
        if not path:
            continue
        try:
            hf_hub_download(
                repo_id=repo_id,
                repo_type="dataset",
                filename=path,
                revision=resolved_revision,
                local_dir=str(local_dir),
                local_dir_use_symlinks=False,
            )
            downloaded.append({"path": path, "size": int(item.get("size") or 0)})
        except Exception as exc:  # noqa: BLE001
            return {
                "status": "FAILED",
                "error": f"download failed for {path}: {type(exc).__name__}: {exc}",
                "revision": resolved_revision,
                "download_plan": plan,
                "downloaded_files": downloaded,
            }

    removed = _prune_unplanned_parquets(local_dir, planned_paths) if prune_unplanned else []

    return {
        "status": "SUCCESS",
        "revision": resolved_revision,
        "download_plan": plan,
        "downloaded_files": downloaded,
        "pruned_extraneous_parquets": removed,
        "local_dir": str(local_dir),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Acquire a benchmark dataset (bounded HuggingFace download).")
    parser.add_argument("--data-root", type=Path, default=Path("/workspace/data"))
    parser.add_argument("--output", type=Path, default=Path("/workspace/dataset_provenance.json"))
    parser.add_argument("--repo-id", type=str, default="")
    parser.add_argument("--min-joints", type=int, default=6)
    parser.add_argument("--require-real", action="store_true")
    parser.add_argument("--include-namespace", action="store_true", help="Include org/user in local dataset dir name.")
    parser.add_argument("--revision", type=str, default="", help="Optional HF revision (commit sha, branch, or tag).")
    parser.add_argument("--max-parquet-files", type=int, default=DEFAULT_MAX_PARQUET_FILES)
    parser.add_argument("--max-total-bytes", type=int, default=DEFAULT_MAX_TOTAL_BYTES)
    parser.add_argument(
        "--no-prune-unplanned",
        action="store_true",
        help="Do not delete parquet files that were not part of the download plan.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    provenance: dict[str, object] = {"attempts": [], "selected": None, "timestamp": time.time()}
    prune_unplanned = not args.no_prune_unplanned
    revision = args.revision.strip() or None
    repo_ids = [args.repo_id.strip()] if args.repo_id.strip() else list(CANDIDATES)

    for repo_id in repo_ids:
        try:
            local_dir = _choose_local_dir(data_root=args.data_root, repo_id=repo_id, include_namespace=args.include_namespace)
            download = _download_dataset_partial(
                repo_id,
                local_dir=local_dir,
                revision=revision,
                max_parquet_files=int(args.max_parquet_files),
                max_total_bytes=int(args.max_total_bytes),
                prune_unplanned=prune_unplanned,
            )
            if download.get("status") != "SUCCESS":
                provenance["attempts"].append({"repo_id": repo_id, "status": f"FAILED: {download.get('error')}"})
                continue

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
                "revision": str(download.get("revision") or ""),
                "download_plan": download.get("download_plan", {}),
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
                    "revision": str(download.get("revision") or ""),
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
