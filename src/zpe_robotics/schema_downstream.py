"""Downstream utility checks for movement-schema gates."""

from __future__ import annotations

import zlib
from dataclasses import dataclass
from typing import Callable

import numpy as np

from .schema import MovementSchemaV1, resample_trajectory
from .schema_baselines import canonical_flatten, dct_lowpass_vector, fft_lowpass_vector, fmp_vector
from .schema_metrics import rmse, velocity_rmse
from .utils import stable_json_dumps


Vectorizer = Callable[[np.ndarray], np.ndarray]


@dataclass(frozen=True)
class SelectionEvaluation:
    name: str
    budget_per_class: int | str
    selected_indices: dict[str, list[int]]
    selected_demo_count: int
    model_zlib_bytes: int
    action_rmse_mean: float
    action_velocity_rmse_mean: float
    task_success_proxy: float
    rows: list[dict[str, object]]

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "budget_per_class": self.budget_per_class,
            "selected_indices": self.selected_indices,
            "selected_demo_count": self.selected_demo_count,
            "model_zlib_bytes": self.model_zlib_bytes,
            "action_rmse_mean": self.action_rmse_mean,
            "action_velocity_rmse_mean": self.action_velocity_rmse_mean,
            "task_success_proxy": self.task_success_proxy,
            "utility_per_zlib_byte": self.task_success_proxy / max(1, self.model_zlib_bytes),
            "rows": self.rows,
        }


def action_feature_indices(feature_names: tuple[str, ...]) -> tuple[int, ...]:
    indices = tuple(idx for idx, name in enumerate(feature_names) if name.startswith("actions:"))
    if not indices:
        raise ValueError("no action feature fields found")
    return indices


def select_schema_central(
    grouped_train: dict[str, list[np.ndarray]],
    schemas: dict[str, MovementSchemaV1],
    budget: int | str,
) -> dict[str, list[int]]:
    selected: dict[str, list[int]] = {}
    for label, trajectories in grouped_train.items():
        count = _budget_count(budget, len(trajectories))
        scored = [(idx, schemas[label].score_demo(trajectory).distance) for idx, trajectory in enumerate(trajectories)]
        selected[label] = [idx for idx, _ in sorted(scored, key=lambda item: (item[1], item[0]))[:count]]
    return selected


def select_vector_central(
    grouped_train: dict[str, list[np.ndarray]],
    vectorizer: Vectorizer,
    budget: int | str,
) -> dict[str, list[int]]:
    selected: dict[str, list[int]] = {}
    for label, trajectories in grouped_train.items():
        count = _budget_count(budget, len(trajectories))
        vectors = np.stack([vectorizer(trajectory) for trajectory in trajectories], axis=0)
        centroid = np.mean(vectors, axis=0)
        distances = np.sqrt(np.mean(np.square(vectors - centroid[None, :]), axis=1))
        selected[label] = [int(idx) for idx in np.argsort(distances, kind="stable")[:count]]
    return selected


def select_medoid_farthest(
    grouped_train: dict[str, list[np.ndarray]],
    budget: int | str,
) -> dict[str, list[int]]:
    selected: dict[str, list[int]] = {}
    for label, trajectories in grouped_train.items():
        count = _budget_count(budget, len(trajectories))
        vectors = np.stack([canonical_flatten(trajectory) for trajectory in trajectories], axis=0)
        selected[label] = _medoid_farthest_indices(vectors, count)
    return selected


def select_random(
    grouped_train: dict[str, list[np.ndarray]],
    budget: int | str,
    seed: int,
) -> dict[str, list[int]]:
    rng = np.random.default_rng(seed)
    selected: dict[str, list[int]] = {}
    for label, trajectories in grouped_train.items():
        count = _budget_count(budget, len(trajectories))
        selected[label] = [int(idx) for idx in rng.permutation(len(trajectories))[:count]]
    return selected


def standard_selector_specs() -> tuple[tuple[str, Vectorizer], ...]:
    return (
        ("mean_central", canonical_flatten),
        ("fft_lowpass_central", fft_lowpass_vector),
        ("dct_lowpass_central", dct_lowpass_vector),
        ("fmp_fourier_central", fmp_vector),
    )


def evaluate_demo_selection(
    name: str,
    grouped_train: dict[str, list[np.ndarray]],
    test_items: list[tuple[str, str, np.ndarray]],
    selected_indices: dict[str, list[int]],
    feature_indices: tuple[int, ...],
    frame_count: int,
    selector_overhead_bytes: int = 0,
    budget: int | str = "all",
) -> SelectionEvaluation:
    predicted_by_label = {}
    for label, indices in selected_indices.items():
        if not indices:
            raise ValueError(f"selector {name!r} selected no demos for {label!r}")
        selected = [
            _feature_trajectory(grouped_train[label][idx], feature_indices, frame_count)
            for idx in indices
        ]
        predicted_by_label[label] = np.mean(np.stack(selected, axis=0), axis=0)

    rows = []
    rmses = []
    velocity_rmses = []
    for true_label, episode_id, trajectory in test_items:
        reference = _feature_trajectory(trajectory, feature_indices, frame_count)
        predicted = predicted_by_label[true_label]
        action_rmse = rmse(reference, predicted)
        action_velocity_rmse = velocity_rmse(reference, predicted)
        rows.append(
            {
                "episode_id": episode_id,
                "true_label": true_label,
                "action_rmse": action_rmse,
                "action_velocity_rmse": action_velocity_rmse,
            }
        )
        rmses.append(action_rmse)
        velocity_rmses.append(action_velocity_rmse)

    action_rmse_mean = float(np.mean(rmses)) if rmses else 0.0
    velocity_rmse_mean = float(np.mean(velocity_rmses)) if velocity_rmses else 0.0
    storage = selected_demo_storage(grouped_train, selected_indices)
    model_zlib_bytes = int(storage["total_zlib_plus_metadata_bytes"]) + int(selector_overhead_bytes)
    return SelectionEvaluation(
        name=name,
        budget_per_class=budget,
        selected_indices=selected_indices,
        selected_demo_count=sum(len(rows) for rows in selected_indices.values()),
        model_zlib_bytes=model_zlib_bytes,
        action_rmse_mean=action_rmse_mean,
        action_velocity_rmse_mean=velocity_rmse_mean,
        task_success_proxy=float(1.0 / (1.0 + action_rmse_mean)),
        rows=rows,
    )


def selected_demo_storage(
    grouped_train: dict[str, list[np.ndarray]],
    selected_indices: dict[str, list[int]],
) -> dict[str, object]:
    by_label = {}
    raw = 0
    compressed = 0
    metadata_bytes = 0
    count = 0
    for label, indices in selected_indices.items():
        label_raw = 0
        label_compressed = 0
        label_metadata = 0
        for idx in indices:
            trajectory = np.asarray(grouped_train[label][idx], dtype=np.float32)
            metadata = {
                "action_label": label,
                "local_index": int(idx),
                "frame_count": int(trajectory.shape[0]),
                "feature_count": int(trajectory.shape[1]),
                "encoding": "float32_original_trajectory",
            }
            meta_bytes = len(stable_json_dumps(metadata).encode("utf-8"))
            body = trajectory.tobytes(order="C")
            label_raw += len(body)
            label_compressed += len(zlib.compress(body, level=9))
            label_metadata += meta_bytes
            count += 1
        by_label[label] = {
            "retained_demo_count": len(indices),
            "raw_float32_bytes": label_raw,
            "zlib_float32_bytes": label_compressed,
            "metadata_bytes": label_metadata,
            "total_raw_plus_metadata_bytes": label_raw + label_metadata,
            "total_zlib_plus_metadata_bytes": label_compressed + label_metadata,
        }
        raw += label_raw
        compressed += label_compressed
        metadata_bytes += label_metadata

    return {
        "retained_demo_count": count,
        "raw_float32_bytes": raw,
        "zlib_float32_bytes": compressed,
        "metadata_bytes": metadata_bytes,
        "total_raw_plus_metadata_bytes": raw + metadata_bytes,
        "total_zlib_plus_metadata_bytes": compressed + metadata_bytes,
        "by_label": by_label,
    }


def selection_summary(evaluations: list[SelectionEvaluation]) -> dict[str, object]:
    rows = [evaluation.to_dict() for evaluation in evaluations]
    zpe_rows = [row for row in rows if row["name"] == "schema_selected"]
    baseline_rows = [row for row in rows if row["name"] != "schema_selected"]
    best_zpe = min(zpe_rows, key=lambda row: float(row["action_rmse_mean"])) if zpe_rows else None
    best_baseline = min(baseline_rows, key=lambda row: float(row["action_rmse_mean"])) if baseline_rows else None
    relative_improvement = 0.0
    if best_zpe and best_baseline:
        baseline_rmse = float(best_baseline["action_rmse_mean"])
        relative_improvement = (baseline_rmse - float(best_zpe["action_rmse_mean"])) / max(1.0e-12, baseline_rmse)
    return {
        "rows": rows,
        "best_schema_selected": best_zpe,
        "best_non_schema": best_baseline,
        "schema_relative_improvement_vs_best_non_schema": float(relative_improvement),
    }


def _feature_trajectory(
    trajectory: np.ndarray,
    feature_indices: tuple[int, ...],
    frame_count: int,
) -> np.ndarray:
    return resample_trajectory(trajectory, frame_count)[:, feature_indices].astype(np.float64, copy=False)


def _budget_count(budget: int | str, available: int) -> int:
    if budget == "all":
        return available
    return max(1, min(int(budget), available))


def _medoid_farthest_indices(vectors: np.ndarray, count: int) -> list[int]:
    if count >= vectors.shape[0]:
        return list(range(vectors.shape[0]))
    distances = _pairwise_rmse(vectors)
    selected = [int(np.argmin(np.sum(distances, axis=1)))]
    while len(selected) < count:
        min_distance = np.min(distances[:, selected], axis=1)
        min_distance[selected] = -1.0
        selected.append(int(np.argmax(min_distance)))
    return selected


def _pairwise_rmse(matrix: np.ndarray) -> np.ndarray:
    gram = matrix @ matrix.T
    square_norm = np.sum(np.square(matrix), axis=1)
    distances = square_norm[:, None] + square_norm[None, :] - 2.0 * gram
    distances = np.maximum(distances / matrix.shape[1], 0.0)
    return np.sqrt(distances)
