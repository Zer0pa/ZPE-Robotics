"""Helpers for qualifying and loading Phase 9 enterprise benchmark datasets."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

import numpy as np


DEFAULT_FIELD_PREFERENCE = ("observation.state", "action")


@dataclass(frozen=True)
class DatasetQualification:
    repo_id: str
    path: Path
    parquet_count: int
    selected_field: str | None
    joint_count: int
    fps: float | None
    total_episodes: int | None
    total_frames: int | None
    is_real: bool
    qualifies: bool
    reason: str


def read_dataset_info(dataset_root: Path) -> dict[str, Any]:
    info_path = dataset_root / "meta" / "info.json"
    if not info_path.exists():
        return {}
    return json.loads(info_path.read_text(encoding="utf-8"))


def list_data_parquet_files(dataset_root: Path) -> list[Path]:
    data_root = dataset_root / "data"
    if not data_root.exists():
        return []
    return sorted(data_root.rglob("*.parquet"))


def _field_shape(info: dict[str, Any], field_name: str) -> int:
    features = info.get("features") or {}
    field = features.get(field_name) or {}
    shape = field.get("shape") or []
    if not shape:
        return 0
    width = shape[0]
    return int(width) if isinstance(width, int | float) else 0


def _field_fps(info: dict[str, Any], field_name: str) -> float | None:
    features = info.get("features") or {}
    field = features.get(field_name) or {}
    fps = field.get("fps")
    if fps is None:
        fps = info.get("fps")
    return float(fps) if isinstance(fps, int | float) else None


def select_joint_field(
    info: dict[str, Any],
    *,
    min_joints: int,
    field_preference: tuple[str, ...] = DEFAULT_FIELD_PREFERENCE,
) -> tuple[str | None, int]:
    for field_name in field_preference:
        width = _field_shape(info, field_name)
        if width >= min_joints:
            return field_name, width

    fallback_name = ""
    fallback_width = 0
    for field_name in field_preference:
        width = _field_shape(info, field_name)
        if width > fallback_width:
            fallback_name = field_name
            fallback_width = width
    if fallback_width > 0:
        return fallback_name, fallback_width
    return None, 0


def _is_real_dataset(repo_id: str) -> bool:
    lower = repo_id.lower()
    return "real" in lower and "_sim_" not in lower


def qualify_dataset(
    dataset_root: Path,
    *,
    repo_id: str,
    min_joints: int,
    require_real: bool,
) -> DatasetQualification:
    data_files = list_data_parquet_files(dataset_root)
    info = read_dataset_info(dataset_root)
    selected_field, joint_count = select_joint_field(info, min_joints=min_joints)
    is_real = _is_real_dataset(repo_id)
    fps = _field_fps(info, selected_field or DEFAULT_FIELD_PREFERENCE[0]) if selected_field else None
    total_episodes = info.get("total_episodes")
    total_frames = info.get("total_frames")

    if not data_files:
        return DatasetQualification(
            repo_id=repo_id,
            path=dataset_root,
            parquet_count=0,
            selected_field=None,
            joint_count=0,
            fps=fps,
            total_episodes=int(total_episodes) if isinstance(total_episodes, int | float) else None,
            total_frames=int(total_frames) if isinstance(total_frames, int | float) else None,
            is_real=is_real,
            qualifies=False,
            reason="NO_DATA_PARQUET",
        )

    if joint_count < min_joints or selected_field is None:
        return DatasetQualification(
            repo_id=repo_id,
            path=dataset_root,
            parquet_count=len(data_files),
            selected_field=selected_field,
            joint_count=joint_count,
            fps=fps,
            total_episodes=int(total_episodes) if isinstance(total_episodes, int | float) else None,
            total_frames=int(total_frames) if isinstance(total_frames, int | float) else None,
            is_real=is_real,
            qualifies=False,
            reason=f"INSUFFICIENT_JOINT_DIM_LT_{min_joints}",
        )

    if require_real and not is_real:
        return DatasetQualification(
            repo_id=repo_id,
            path=dataset_root,
            parquet_count=len(data_files),
            selected_field=selected_field,
            joint_count=joint_count,
            fps=fps,
            total_episodes=int(total_episodes) if isinstance(total_episodes, int | float) else None,
            total_frames=int(total_frames) if isinstance(total_frames, int | float) else None,
            is_real=is_real,
            qualifies=False,
            reason="NOT_REAL_DATASET",
        )

    return DatasetQualification(
        repo_id=repo_id,
        path=dataset_root,
        parquet_count=len(data_files),
        selected_field=selected_field,
        joint_count=joint_count,
        fps=fps,
        total_episodes=int(total_episodes) if isinstance(total_episodes, int | float) else None,
        total_frames=int(total_frames) if isinstance(total_frames, int | float) else None,
        is_real=is_real,
        qualifies=True,
        reason="QUALIFIED",
    )


def _episode_ids_to_numpy(values: list[Any], *, row_count: int) -> np.ndarray:
    if not values:
        return np.zeros(row_count, dtype=np.int64)
    return np.asarray(values, dtype=np.int64)


def load_joint_rows(dataset_root: Path, *, field_name: str) -> tuple[np.ndarray, np.ndarray]:
    try:
        import pyarrow.parquet as pq
    except Exception as exc:
        raise RuntimeError(f"pyarrow unavailable: {exc}") from exc

    matrices: list[np.ndarray] = []
    episode_ids: list[np.ndarray] = []
    for parquet_path in list_data_parquet_files(dataset_root):
        table = pq.read_table(parquet_path, columns=[field_name, "episode_index"])
        if table.num_rows == 0:
            continue
        field_values = table[field_name].to_pylist()
        matrix = np.asarray(field_values, dtype=np.float32)
        if matrix.ndim != 2:
            raise ValueError(f"{parquet_path} field {field_name} did not decode to a 2D float matrix")
        matrices.append(matrix)
        ids = _episode_ids_to_numpy(table["episode_index"].to_pylist(), row_count=matrix.shape[0])
        if ids.shape[0] != matrix.shape[0]:
            raise ValueError(f"{parquet_path} episode index row count mismatch for field {field_name}")
        episode_ids.append(ids)

    if not matrices:
        raise ValueError(f"no usable {field_name} rows found under {dataset_root}")

    return np.concatenate(matrices, axis=0), np.concatenate(episode_ids, axis=0)


def build_sample_matrix(rows: np.ndarray, *, target_frames: int) -> np.ndarray:
    if rows.shape[0] < 8:
        padding = np.repeat(rows[-1:, :], 8 - rows.shape[0], axis=0)
        rows = np.concatenate([rows, padding], axis=0)
    if rows.shape[0] >= target_frames:
        return rows[:target_frames, :].astype(np.float32, copy=False)
    padding = np.repeat(rows[-1:, :], target_frames - rows.shape[0], axis=0)
    return np.concatenate([rows, padding], axis=0).astype(np.float32, copy=False)


def load_joint_dataset_sample(
    dataset_root: Path,
    *,
    repo_id: str,
    target_frames: int,
    min_joints: int = 1,
) -> tuple[np.ndarray, dict[str, Any]]:
    qualification = qualify_dataset(dataset_root, repo_id=repo_id, min_joints=min_joints, require_real=False)
    if qualification.selected_field is None:
        raise ValueError(f"dataset {repo_id} has no usable joint field")

    rows, episode_ids = load_joint_rows(dataset_root, field_name=qualification.selected_field)
    sample = build_sample_matrix(rows, target_frames=target_frames)
    unique_episode_count = int(np.unique(episode_ids).shape[0]) if episode_ids.size else 0

    meta = {
        "source": "dataset",
        "dataset_root": str(dataset_root),
        "repo_id": repo_id,
        "selected_field": qualification.selected_field,
        "joint_count": qualification.joint_count,
        "fps": qualification.fps,
        "is_real_dataset": qualification.is_real,
        "episode_count_total": unique_episode_count,
        "frame_count_total": int(rows.shape[0]),
        "qualified_reason": qualification.reason,
        "sample_shape": list(sample.shape),
    }
    if qualification.total_episodes is not None:
        meta["declared_total_episodes"] = qualification.total_episodes
    if qualification.total_frames is not None:
        meta["declared_total_frames"] = qualification.total_frames
    return sample, meta


def load_episode_matrices(
    dataset_root: Path,
    *,
    repo_id: str,
    min_joints: int = 1,
) -> tuple[list[np.ndarray], dict[str, Any]]:
    qualification = qualify_dataset(dataset_root, repo_id=repo_id, min_joints=min_joints, require_real=False)
    if qualification.selected_field is None:
        raise ValueError(f"dataset {repo_id} has no usable joint field")

    rows, episode_ids = load_joint_rows(dataset_root, field_name=qualification.selected_field)
    unique_ids = np.unique(episode_ids)
    episodes = [rows[episode_ids == episode_id].astype(np.float32, copy=False) for episode_id in unique_ids]
    meta = {
        "dataset_root": str(dataset_root),
        "repo_id": repo_id,
        "selected_field": qualification.selected_field,
        "joint_count": qualification.joint_count,
        "fps": qualification.fps,
        "is_real_dataset": qualification.is_real,
        "episode_count_total": len(episodes),
        "frame_count_total": int(rows.shape[0]),
        "qualified_reason": qualification.reason,
    }
    if qualification.total_episodes is not None:
        meta["declared_total_episodes"] = qualification.total_episodes
    if qualification.total_frames is not None:
        meta["declared_total_frames"] = qualification.total_frames
    return episodes, meta
