"""Baseline models for movement-schema retrieval gates."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from .schema import canonicalize_trajectory


Vectorizer = Callable[[np.ndarray], np.ndarray]


@dataclass(frozen=True)
class BaselineScore:
    label: str
    distance: float


class ActionCentroidBaseline:
    """Action classifier using centroids in a fixed representation space."""

    def __init__(self, name: str, vectorizer: Vectorizer) -> None:
        self.name = name
        self._vectorizer = vectorizer
        self._centroids: dict[str, np.ndarray] = {}
        self._variances: dict[str, np.ndarray] = {}

    def fit(self, grouped: dict[str, list[np.ndarray]]) -> "ActionCentroidBaseline":
        if not grouped:
            raise ValueError("baseline requires at least one action group")
        centroids: dict[str, np.ndarray] = {}
        variances: dict[str, np.ndarray] = {}
        for label, trajectories in grouped.items():
            if not trajectories:
                raise ValueError(f"action group {label!r} is empty")
            vectors = np.stack([self._vectorizer(traj) for traj in trajectories], axis=0)
            centroids[label] = np.mean(vectors, axis=0)
            variance = np.var(vectors, axis=0, ddof=1) if len(vectors) > 1 else np.ones(vectors.shape[1])
            variances[label] = np.where(variance < 1.0e-6, 1.0e-6, variance)
        self._centroids = centroids
        self._variances = variances
        return self

    def score(self, trajectory: np.ndarray) -> list[BaselineScore]:
        vector = self._vectorizer(trajectory)
        scores = []
        for label, centroid in self._centroids.items():
            delta = vector - centroid
            distance = float(np.sqrt(np.mean(np.square(delta) / self._variances[label])))
            scores.append(BaselineScore(label=label, distance=distance))
        return sorted(scores, key=lambda score: score.distance)

    def predict(self, trajectory: np.ndarray) -> str:
        return self.score(trajectory)[0].label


class NearestDemoBaseline:
    """Non-parametric nearest-demo baseline over canonicalized trajectories."""

    name = "nearest_demo"

    def __init__(self) -> None:
        self._examples: list[tuple[str, np.ndarray]] = []

    def fit(self, grouped: dict[str, list[np.ndarray]]) -> "NearestDemoBaseline":
        examples = []
        for label, trajectories in grouped.items():
            for trajectory in trajectories:
                examples.append((label, canonical_flatten(trajectory)))
        if not examples:
            raise ValueError("nearest-demo baseline requires examples")
        self._examples = examples
        return self

    def score(self, trajectory: np.ndarray) -> list[BaselineScore]:
        vector = canonical_flatten(trajectory)
        best_by_label: dict[str, float] = {}
        for label, example in self._examples:
            distance = float(np.sqrt(np.mean(np.square(vector - example))))
            best_by_label[label] = min(distance, best_by_label.get(label, float("inf")))
        return sorted(
            [BaselineScore(label=label, distance=distance) for label, distance in best_by_label.items()],
            key=lambda score: score.distance,
        )

    def predict(self, trajectory: np.ndarray) -> str:
        return self.score(trajectory)[0].label


class GlobalPCABaseline:
    """Global PCA centroid baseline shared across all actions."""

    name = "global_pca"

    def __init__(self, component_count: int = 8) -> None:
        self.component_count = component_count
        self._mean: np.ndarray | None = None
        self._components: np.ndarray | None = None
        self._centroids: dict[str, np.ndarray] = {}
        self._variances: dict[str, np.ndarray] = {}

    def fit(self, grouped: dict[str, list[np.ndarray]]) -> "GlobalPCABaseline":
        labels = []
        vectors = []
        for label, trajectories in grouped.items():
            for trajectory in trajectories:
                labels.append(label)
                vectors.append(canonical_flatten(trajectory))
        if len(vectors) < 2:
            raise ValueError("global PCA baseline requires at least two demonstrations")

        matrix = np.stack(vectors, axis=0)
        mean = np.mean(matrix, axis=0)
        centered = matrix - mean
        _, _, vt = np.linalg.svd(centered, full_matrices=False)
        components = vt[: max(1, min(self.component_count, vt.shape[0]))]
        latent = centered @ components.T

        centroids: dict[str, np.ndarray] = {}
        variances: dict[str, np.ndarray] = {}
        for label in sorted(set(labels)):
            rows = latent[[idx for idx, row_label in enumerate(labels) if row_label == label]]
            centroids[label] = np.mean(rows, axis=0)
            variance = np.var(rows, axis=0, ddof=1) if len(rows) > 1 else np.ones(rows.shape[1])
            variances[label] = np.where(variance < 1.0e-6, 1.0e-6, variance)

        self._mean = mean
        self._components = components
        self._centroids = centroids
        self._variances = variances
        return self

    def score(self, trajectory: np.ndarray) -> list[BaselineScore]:
        if self._mean is None or self._components is None:
            raise ValueError("global PCA baseline is not fitted")
        vector = (canonical_flatten(trajectory) - self._mean) @ self._components.T
        scores = []
        for label, centroid in self._centroids.items():
            delta = vector - centroid
            distance = float(np.sqrt(np.mean(np.square(delta) / self._variances[label])))
            scores.append(BaselineScore(label=label, distance=distance))
        return sorted(scores, key=lambda score: score.distance)

    def predict(self, trajectory: np.ndarray) -> str:
        return self.score(trajectory)[0].label


def canonical_flatten(trajectory: np.ndarray, frame_count: int = 128) -> np.ndarray:
    return canonicalize_trajectory(trajectory, frame_count=frame_count).values.reshape(-1)


def fft_lowpass_vector(trajectory: np.ndarray, frame_count: int = 128, keep_coeffs: int = 8) -> np.ndarray:
    values = canonicalize_trajectory(trajectory, frame_count=frame_count).values
    spectrum = np.fft.rfft(values, axis=0)[:keep_coeffs, :]
    return np.concatenate([spectrum.real.reshape(-1), spectrum.imag.reshape(-1)]).astype(np.float64)


def dct_lowpass_vector(trajectory: np.ndarray, frame_count: int = 128, keep_coeffs: int = 8) -> np.ndarray:
    values = canonicalize_trajectory(trajectory, frame_count=frame_count).values
    basis = _dct_ii_basis(frame_count, keep_coeffs)
    coeffs = basis @ values
    return coeffs.reshape(-1).astype(np.float64)


def fmp_vector(trajectory: np.ndarray, frame_count: int = 128, keep_coeffs: int = 12) -> np.ndarray:
    values = canonicalize_trajectory(trajectory, frame_count=frame_count).values
    velocity = np.gradient(values, axis=0)
    spectrum = np.fft.rfft(np.concatenate([values, velocity], axis=1), axis=0)[:keep_coeffs, :]
    return np.concatenate([spectrum.real.reshape(-1), spectrum.imag.reshape(-1)]).astype(np.float64)


def promp_weight_vector(trajectory: np.ndarray, frame_count: int = 128, basis_count: int = 12) -> np.ndarray:
    values = canonicalize_trajectory(trajectory, frame_count=frame_count).values
    phase = np.linspace(0.0, 1.0, frame_count)
    design = _rbf_design(phase, basis_count)
    weights, *_ = np.linalg.lstsq(design, values, rcond=None)
    return weights.reshape(-1).astype(np.float64)


def dmp_weight_vector(trajectory: np.ndarray, frame_count: int = 128, basis_count: int = 12) -> np.ndarray:
    values = canonicalize_trajectory(trajectory, frame_count=frame_count).values
    velocity = np.gradient(values, axis=0)
    acceleration = np.gradient(velocity, axis=0)
    goal = values[-1]
    alpha = 25.0
    beta = alpha / 4.0
    forcing = acceleration - alpha * (beta * (goal - values) - velocity)
    phase = np.linspace(1.0, 0.0, frame_count)
    design = _rbf_design(phase, basis_count)
    weights, *_ = np.linalg.lstsq(design, forcing, rcond=None)
    return weights.reshape(-1).astype(np.float64)


def make_standard_baselines() -> list[ActionCentroidBaseline | NearestDemoBaseline]:
    return [
        ActionCentroidBaseline("mean_trajectory", canonical_flatten),
        ActionCentroidBaseline("fft_lowpass", fft_lowpass_vector),
        ActionCentroidBaseline("dct_lowpass", dct_lowpass_vector),
        GlobalPCABaseline(),
        ActionCentroidBaseline("dmp_rbf_weights", dmp_weight_vector),
        ActionCentroidBaseline("promp_rbf_weights", promp_weight_vector),
        ActionCentroidBaseline("fmp_fourier_weights", fmp_vector),
        NearestDemoBaseline(),
    ]


def _dct_ii_basis(length: int, keep: int) -> np.ndarray:
    n = np.arange(length, dtype=np.float64)
    k = np.arange(keep, dtype=np.float64)[:, None]
    basis = np.cos(np.pi * (n + 0.5) * k / length)
    basis[0, :] *= np.sqrt(1.0 / length)
    if keep > 1:
        basis[1:, :] *= np.sqrt(2.0 / length)
    return basis


def _rbf_design(phase: np.ndarray, basis_count: int) -> np.ndarray:
    centers = np.linspace(float(np.min(phase)), float(np.max(phase)), basis_count)
    width = max(1.0e-6, (centers[1] - centers[0]) ** 2 if basis_count > 1 else 1.0)
    design = np.exp(-0.5 * np.square(phase[:, None] - centers[None, :]) / width)
    row_sums = np.sum(design, axis=1, keepdims=True)
    return design / np.maximum(row_sums, 1.0e-12)
