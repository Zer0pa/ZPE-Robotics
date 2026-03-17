"""Motion primitive generation, indexing, and retrieval metrics."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


PRIMITIVE_LABELS = (
    "reach",
    "grasp",
    "retract",
    "place",
    "push",
    "circular_wipe",
)


@dataclass(frozen=True)
class PrimitiveSample:
    label: str
    trajectory: np.ndarray  # [frames, 2]


TEMPLATE_TO_LABEL = {
    "REACH": "reach",
    "GRASP": "grasp",
    "RETRACT": "retract",
    "PLACE": "place",
    "PUSH": "push",
}


def generate_primitive_corpus(
    seed: int,
    library_per_label: int = 60,
    query_per_label: int = 24,
    length: int = 96,
) -> tuple[list[PrimitiveSample], list[PrimitiveSample]]:
    rng = np.random.default_rng(seed)
    library: list[PrimitiveSample] = []
    queries: list[PrimitiveSample] = []

    for label in PRIMITIVE_LABELS:
        for _ in range(library_per_label):
            library.append(PrimitiveSample(label=label, trajectory=_noisy_pattern(label, length, rng, noise=0.015)))
        for _ in range(query_per_label):
            queries.append(PrimitiveSample(label=label, trajectory=_noisy_pattern(label, length, rng, noise=0.02)))

    return library, queries


def prototype_pattern(label: str, length: int = 96) -> np.ndarray:
    rng = np.random.default_rng(0)
    return _noisy_pattern(label, length, rng, noise=0.0)


def precision_at_k(
    library: list[PrimitiveSample],
    queries: list[PrimitiveSample],
    k: int = 10,
) -> float:
    lib_features = np.stack([shape_signature(item.trajectory) for item in library], axis=0)
    lib_labels = [item.label for item in library]

    precisions = []
    for query in queries:
        q_feat = shape_signature(query.trajectory)
        dist = np.mean(np.square(lib_features - q_feat[None, :]), axis=1)
        topk = np.argsort(dist)[:k]
        hits = sum(1 for idx in topk if lib_labels[idx] == query.label)
        precisions.append(hits / float(k))

    return float(np.mean(precisions))


def confusion_stress(
    library: list[PrimitiveSample],
    seed: int,
    count: int = 80,
    k: int = 10,
) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    lib_features = np.stack([token_histogram(direction_magnitude_tokens(item.trajectory)) for item in library], axis=0)

    false_positives = 0
    for _ in range(count):
        a, b = rng.choice(library, size=2, replace=False)
        if a.label == b.label:
            continue
        alpha = rng.uniform(0.4, 0.6)
        blended = alpha * a.trajectory + (1.0 - alpha) * b.trajectory
        q_feat = token_histogram(direction_magnitude_tokens(blended))
        scores = cosine_similarity_matrix(lib_features, q_feat)
        topk = np.argsort(scores)[-k:][::-1]
        top_labels = {library[idx].label for idx in topk}
        if len(top_labels) < 2:
            false_positives += 1

    trials = max(1, count)
    fpr = false_positives / float(trials)
    return {
        "queries": float(trials),
        "false_positive_rate": float(fpr),
        "pass": bool(fpr <= 0.25),
    }


def direction_magnitude_tokens(path: np.ndarray, magnitude_bins: int = 3) -> np.ndarray:
    arr = np.asarray(path, dtype=np.float64)
    if arr.ndim != 2 or arr.shape[1] != 2:
        raise ValueError("path must be [frames, 2]")
    if arr.shape[0] < 3:
        raise ValueError("path must have >=3 frames")

    delta = np.diff(arr, axis=0)
    angles = np.arctan2(delta[:, 1], delta[:, 0])
    direction = np.floor(((angles + np.pi) / (2.0 * np.pi)) * 8.0).astype(np.int64) % 8

    mag = np.linalg.norm(delta, axis=1)
    q1, q2 = np.quantile(mag, [0.33, 0.66])
    cuts = np.array([q1, q2], dtype=np.float64)
    magnitude = np.digitize(mag, cuts, right=False)
    magnitude = np.clip(magnitude, 0, magnitude_bins - 1)

    vocab_mag = magnitude_bins
    tokens = direction * vocab_mag + magnitude
    return tokens.astype(np.int64)


def token_histogram(tokens: np.ndarray, vocab_size: int = 24) -> np.ndarray:
    hist = np.bincount(tokens, minlength=vocab_size).astype(np.float64)
    denom = np.sum(hist)
    if denom <= 0.0:
        raise ValueError("token histogram denominator is zero")
    return hist / denom


def cosine_similarity_matrix(matrix: np.ndarray, vector: np.ndarray) -> np.ndarray:
    m = np.asarray(matrix, dtype=np.float64)
    v = np.asarray(vector, dtype=np.float64)
    m_norm = np.linalg.norm(m, axis=1)
    v_norm = np.linalg.norm(v)
    denom = np.clip(m_norm * v_norm, 1e-12, None)
    return np.sum(m * v[None, :], axis=1) / denom


def shape_signature(path: np.ndarray) -> np.ndarray:
    arr = np.asarray(path, dtype=np.float64)
    if arr.ndim != 2 or arr.shape[1] != 2:
        raise ValueError("path must be [frames, 2]")
    centered = arr - np.mean(arr, axis=0, keepdims=True)
    scale = np.sqrt(np.mean(np.sum(np.square(centered), axis=1)))
    normalized = centered / max(float(scale), 1.0e-12)
    return normalized.reshape(-1)


def _noisy_pattern(label: str, length: int, rng: np.random.Generator, noise: float) -> np.ndarray:
    t = np.linspace(0.0, 1.0, length, endpoint=False)

    if label == "reach":
        x = 1.2 * t
        y = 0.3 * np.sin(0.6 * np.pi * t) + 0.25 * t
    elif label == "grasp":
        x = 0.7 + 0.04 * np.sin(8.0 * np.pi * t)
        y = 0.5 + 0.04 * np.cos(8.0 * np.pi * t)
    elif label == "retract":
        x = 1.2 - 1.1 * t
        y = 0.45 - 0.2 * t
    elif label == "place":
        x = 0.6 + 0.05 * np.sin(2.0 * np.pi * t)
        y = 0.9 - 0.9 * t
    elif label == "push":
        x = 1.5 * t
        y = 0.22 + 0.03 * np.sin(4.0 * np.pi * t)
    elif label == "circular_wipe":
        x = 0.8 + 0.35 * np.cos(2.0 * np.pi * t)
        y = 0.4 + 0.35 * np.sin(2.0 * np.pi * t)
    else:
        raise ValueError(f"unknown primitive label: {label}")

    stacked = np.stack([x, y], axis=1)
    # Apply affine jitter to prevent location-only baselines from dominating.
    scale = rng.uniform(0.75, 1.25)
    shift = rng.uniform(-0.5, 0.5, size=2)
    stacked = (stacked * scale) + shift[None, :]
    jitter = rng.normal(0.0, noise, size=stacked.shape)
    return stacked + jitter
