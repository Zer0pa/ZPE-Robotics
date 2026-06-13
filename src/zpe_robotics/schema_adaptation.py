"""Generation and adaptation baselines for movement-schema gates."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np

from .schema import MovementSchemaV1, resample_trajectory
from .schema_metrics import endpoint_error, rmse, velocity_rmse


@dataclass(frozen=True)
class AdaptationResult:
    trajectory: np.ndarray
    metadata: dict[str, object]


class AdaptableMovementModel(Protocol):
    name: str
    action_label: str

    def adapt(self, start: np.ndarray, goal: np.ndarray) -> AdaptationResult:
        ...


def primitive_feature_indices(feature_names: tuple[str, ...]) -> tuple[int, ...]:
    preferred_prefixes = (
        "obs/robot0_eef_pos:",
        "obs/robot0_gripper_qpos:",
    )
    indices = tuple(
        idx
        for idx, name in enumerate(feature_names)
        if any(name.startswith(prefix) for prefix in preferred_prefixes)
    )
    return indices if indices else tuple(range(min(5, len(feature_names))))


def primitive_feature_names(feature_names: tuple[str, ...], indices: tuple[int, ...]) -> tuple[str, ...]:
    if not feature_names:
        return tuple(f"feature_{idx}" for idx in indices)
    return tuple(feature_names[idx] for idx in indices)


def prepare_primitive_trajectories(
    trajectories: list[np.ndarray],
    feature_indices: tuple[int, ...],
    frame_count: int,
) -> list[np.ndarray]:
    return [prepare_primitive_trajectory(trajectory, feature_indices, frame_count) for trajectory in trajectories]


def prepare_primitive_trajectory(
    trajectory: np.ndarray,
    feature_indices: tuple[int, ...],
    frame_count: int,
) -> np.ndarray:
    values = resample_trajectory(trajectory, frame_count)
    return values[:, feature_indices].astype(np.float64, copy=False)


def adapt_endpoint_linear(base: np.ndarray, start: np.ndarray, goal: np.ndarray) -> np.ndarray:
    values = np.asarray(base, dtype=np.float64)
    if values.ndim != 2:
        raise ValueError("base trajectory must be 2D")
    start = np.asarray(start, dtype=np.float64)
    goal = np.asarray(goal, dtype=np.float64)
    if start.shape != goal.shape or start.shape != values[0].shape:
        raise ValueError("start/goal shape mismatch")

    shifted = values + (start - values[0])[None, :]
    endpoint_delta = goal - shifted[-1]
    phase = np.linspace(0.0, 1.0, len(shifted))[:, None]
    return shifted + phase * endpoint_delta[None, :]


def adaptation_metrics(reference: np.ndarray, candidate: np.ndarray) -> dict[str, float]:
    return {
        "rmse": rmse(reference, candidate),
        "velocity_rmse": velocity_rmse(reference, candidate),
        "endpoint_error": endpoint_error(reference, candidate),
    }


@dataclass
class MeanTrajectoryAdapter:
    action_label: str
    mean_trajectory: np.ndarray
    name: str = "mean_linear_endpoint"

    def adapt(self, start: np.ndarray, goal: np.ndarray) -> AdaptationResult:
        return AdaptationResult(
            adapt_endpoint_linear(self.mean_trajectory, start, goal),
            {"adaptation": "linear_start_goal_endpoint_correction"},
        )


@dataclass
class DemoReplayAdapter:
    action_label: str
    base_trajectory: np.ndarray
    selected_index: int
    name: str = "medoid_demo_linear_endpoint"

    def adapt(self, start: np.ndarray, goal: np.ndarray) -> AdaptationResult:
        return AdaptationResult(
            adapt_endpoint_linear(self.base_trajectory, start, goal),
            {
                "adaptation": "selected training demonstration plus linear start/goal correction",
                "selected_index": int(self.selected_index),
            },
        )


@dataclass
class FMPAdapter:
    action_label: str
    coeffs: np.ndarray
    frame_count: int
    feature_count: int
    name: str = "fmp_fourier_generation_local"

    @classmethod
    def fit(
        cls,
        action_label: str,
        demonstrations: list[np.ndarray],
        keep_coeffs: int,
    ) -> "FMPAdapter":
        if not demonstrations:
            raise ValueError("FMPAdapter requires demonstrations")
        frame_count, feature_count = demonstrations[0].shape
        spectra = []
        for demo in demonstrations:
            spectra.append(np.fft.rfft(demo, axis=0)[:keep_coeffs])
        return cls(
            action_label=action_label,
            coeffs=np.mean(np.stack(spectra, axis=0), axis=0),
            frame_count=frame_count,
            feature_count=feature_count,
        )

    def adapt(self, start: np.ndarray, goal: np.ndarray) -> AdaptationResult:
        full = np.zeros((self.frame_count // 2 + 1, self.feature_count), dtype=np.complex128)
        full[: len(self.coeffs)] = self.coeffs
        base = np.fft.irfft(full, n=self.frame_count, axis=0)
        return AdaptationResult(
            adapt_endpoint_linear(base, start, goal),
            {
                "adaptation": "Fourier mean reconstruction plus linear start/goal correction",
                "external_package": False,
            },
        )


@dataclass
class ZPESchemaAdapter:
    action_label: str
    schema: MovementSchemaV1
    feature_indices: tuple[int, ...]
    name: str = "zpe_schema_initializer"

    def adapt(self, start: np.ndarray, goal: np.ndarray) -> AdaptationResult:
        canonical_center = self.schema.central_form * self.schema.feature_scale + self.schema.feature_offset
        relative = canonical_center[:, self.feature_indices]
        base = relative + start[None, :]
        return AdaptationResult(
            adapt_endpoint_linear(base, start, goal),
            {
                "adaptation": "MovementSchemaV1 relative central form plus linear start/goal correction",
                "component_count": int(self.schema.components.shape[0]),
                "demo_count": int(self.schema.demo_count),
            },
        )


@dataclass
class ExternalDMPAdapter:
    action_label: str
    dmp: object
    frame_count: int
    name: str = "external_dmp"

    @classmethod
    def fit(
        cls,
        action_label: str,
        demonstrations: list[np.ndarray],
        n_weights_per_dim: int,
    ) -> "ExternalDMPAdapter":
        from movement_primitives.dmp import DMP

        if not demonstrations:
            raise ValueError("ExternalDMPAdapter requires demonstrations")
        mean = np.mean(np.stack(demonstrations, axis=0), axis=0)
        frame_count, feature_count = mean.shape
        time = np.linspace(0.0, 1.0, frame_count)
        dmp = DMP(
            n_dims=feature_count,
            execution_time=1.0,
            dt=1.0 / max(1, frame_count - 1),
            n_weights_per_dim=n_weights_per_dim,
            int_dt=0.001,
            smooth_scaling=True,
        )
        dmp.imitate(time, mean, regularization_coefficient=1.0e-8)
        return cls(action_label=action_label, dmp=dmp, frame_count=frame_count)

    def adapt(self, start: np.ndarray, goal: np.ndarray) -> AdaptationResult:
        self.dmp.configure(start_y=start, goal_y=goal)
        _, values = self.dmp.open_loop(run_t=1.0)
        values = _resample_if_needed(values, self.frame_count)
        return AdaptationResult(
            values,
            {
                "adaptation": "external movement_primitives DMP start_y/goal_y configuration",
                "external_package": "movement_primitives",
            },
        )


@dataclass
class ExternalProMPAdapter:
    action_label: str
    promp: object
    frame_count: int
    name: str = "external_promp"

    @classmethod
    def fit(
        cls,
        action_label: str,
        demonstrations: list[np.ndarray],
        n_weights_per_dim: int,
        n_iter: int,
    ) -> "ExternalProMPAdapter":
        from movement_primitives.promp import ProMP

        if not demonstrations:
            raise ValueError("ExternalProMPAdapter requires demonstrations")
        values = np.stack(demonstrations, axis=0)
        frame_count = values.shape[1]
        time = np.linspace(0.0, 1.0, frame_count)
        times = np.tile(time[None, :], (values.shape[0], 1))
        promp = ProMP(n_dims=values.shape[2], n_weights_per_dim=n_weights_per_dim)
        promp.imitate(times, values, n_iter=n_iter, min_delta=1.0e-4)
        return cls(action_label=action_label, promp=promp, frame_count=frame_count)

    def adapt(self, start: np.ndarray, goal: np.ndarray) -> AdaptationResult:
        time = np.linspace(0.0, 1.0, self.frame_count)
        adapted = self.promp.condition_position(start, t=0.0).condition_position(goal, t=1.0)
        return AdaptationResult(
            adapted.mean_trajectory(time),
            {
                "adaptation": "external movement_primitives ProMP endpoint conditioning",
                "external_package": "movement_primitives",
            },
        )


def build_adaptation_models(
    grouped_train: dict[str, list[np.ndarray]],
    schemas: dict[str, MovementSchemaV1],
    feature_indices: tuple[int, ...],
    frame_count: int,
    dmp_weights: int = 16,
    promp_weights: int = 10,
    promp_iter: int = 50,
    fmp_coeffs: int = 16,
) -> tuple[dict[str, dict[str, AdaptableMovementModel]], dict[str, str]]:
    models: dict[str, dict[str, AdaptableMovementModel]] = {
        "zpe_schema_initializer": {},
        "mean_linear_endpoint": {},
        "medoid_demo_linear_endpoint": {},
        "fmp_fourier_generation_local": {},
    }
    failures: dict[str, str] = {}
    primitive_train = {
        label: prepare_primitive_trajectories(trajectories, feature_indices, frame_count)
        for label, trajectories in grouped_train.items()
    }
    for label, demos in primitive_train.items():
        models["zpe_schema_initializer"][label] = ZPESchemaAdapter(label, schemas[label], feature_indices)
        models["mean_linear_endpoint"][label] = MeanTrajectoryAdapter(label, np.mean(np.stack(demos, axis=0), axis=0))
        medoid_idx = _medoid_index(demos)
        models["medoid_demo_linear_endpoint"][label] = DemoReplayAdapter(label, demos[medoid_idx], medoid_idx)
        models["fmp_fourier_generation_local"][label] = FMPAdapter.fit(label, demos, keep_coeffs=fmp_coeffs)

    try:
        models["external_dmp"] = {
            label: ExternalDMPAdapter.fit(label, demos, n_weights_per_dim=dmp_weights)
            for label, demos in primitive_train.items()
        }
    except Exception as exc:  # pragma: no cover - receipt path depends on optional package
        failures["external_dmp"] = str(exc)

    try:
        models["external_promp"] = {
            label: ExternalProMPAdapter.fit(label, demos, n_weights_per_dim=promp_weights, n_iter=promp_iter)
            for label, demos in primitive_train.items()
        }
    except Exception as exc:  # pragma: no cover - receipt path depends on optional package
        failures["external_promp"] = str(exc)

    return models, failures


def evaluate_adaptation_models(
    models: dict[str, dict[str, AdaptableMovementModel]],
    test_trajectories: list[tuple[str, str, np.ndarray]],
) -> dict[str, dict[str, object]]:
    payload = {}
    for model_name, label_models in models.items():
        rows = []
        true_label_metrics = []
        for true_label, episode_id, reference in test_trajectories:
            start = reference[0]
            goal = reference[-1]
            scores = {}
            per_label = {}
            for candidate_label, model in label_models.items():
                result = model.adapt(start, goal)
                metrics = adaptation_metrics(reference, result.trajectory)
                scores[candidate_label] = metrics["rmse"]
                per_label[candidate_label] = metrics
            predicted_label = min(scores, key=scores.get)
            true_label_metrics.append(per_label[true_label])
            rows.append(
                {
                    "episode_id": episode_id,
                    "true_label": true_label,
                    "predicted_label": predicted_label,
                    "scores": scores,
                    "true_label_metrics": per_label[true_label],
                }
            )

        payload[model_name] = {
            "rows": rows,
            "assignment_accuracy": _accuracy(rows),
            "true_label_generation_rmse_mean": _mean_metric(true_label_metrics, "rmse"),
            "true_label_velocity_rmse_mean": _mean_metric(true_label_metrics, "velocity_rmse"),
            "true_label_endpoint_error_mean": _mean_metric(true_label_metrics, "endpoint_error"),
        }
    return payload


def _resample_if_needed(values: np.ndarray, frame_count: int) -> np.ndarray:
    if values.shape[0] == frame_count:
        return np.asarray(values, dtype=np.float64)
    return resample_trajectory(np.asarray(values, dtype=np.float64), frame_count)


def _accuracy(rows: list[dict[str, object]]) -> float:
    if not rows:
        return 0.0
    correct = sum(1 for row in rows if row["true_label"] == row["predicted_label"])
    return float(correct / len(rows))


def _mean_metric(rows: list[dict[str, float]], key: str) -> float:
    if not rows:
        return 0.0
    return float(np.mean([row[key] for row in rows]))


def _medoid_index(demos: list[np.ndarray]) -> int:
    matrix = np.stack([demo.reshape(-1) for demo in demos], axis=0)
    gram = matrix @ matrix.T
    square_norm = np.sum(np.square(matrix), axis=1)
    distances = square_norm[:, None] + square_norm[None, :] - 2.0 * gram
    distances = np.maximum(distances / matrix.shape[1], 0.0)
    return int(np.argmin(np.sum(np.sqrt(distances), axis=1)))
