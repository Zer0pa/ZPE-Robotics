"""VLA-token quality evaluation against baseline tokenizers."""

from __future__ import annotations

from collections import defaultdict

import numpy as np

from .primitives import PRIMITIVE_LABELS, PrimitiveSample


def evaluate_token_quality(dataset: list[PrimitiveSample]) -> dict[str, float | bool]:
    by_label: dict[str, list[PrimitiveSample]] = defaultdict(list)
    for sample in dataset:
        by_label[sample.label].append(sample)

    train: list[PrimitiveSample] = []
    test: list[PrimitiveSample] = []
    for label in PRIMITIVE_LABELS:
        samples = by_label[label]
        split = max(1, int(0.7 * len(samples)))
        train.extend(samples[:split])
        test.extend(samples[split:])

    zpe_acc = _centroid_accuracy(train, test, method="zpe")
    naive_acc = _centroid_accuracy(train, test, method="naive")
    dct_acc = _centroid_accuracy(train, test, method="dct")

    delta = zpe_acc - naive_acc
    return {
        "metric": "centroid_accuracy",
        "zpe_token_accuracy": float(zpe_acc),
        "naive_binning_accuracy": float(naive_acc),
        "fast_dct_proxy_accuracy": float(dct_acc),
        "delta_vs_naive": float(delta),
        "pass": bool(delta >= 0.0),
    }


def _centroid_accuracy(train: list[PrimitiveSample], test: list[PrimitiveSample], method: str) -> float:
    centroids: dict[str, np.ndarray] = {}

    for label in PRIMITIVE_LABELS:
        rows = [
            _extract_features(sample.trajectory, method=method)
            for sample in train
            if sample.label == label
        ]
        if not rows:
            raise ValueError(f"missing training rows for label={label}")
        centroids[label] = np.mean(np.stack(rows, axis=0), axis=0)

    correct = 0
    for sample in test:
        feat = _extract_features(sample.trajectory, method=method)
        predicted = max(PRIMITIVE_LABELS, key=lambda label: _cosine(centroids[label], feat))
        if predicted == sample.label:
            correct += 1

    return correct / max(1, len(test))


def _extract_features(path: np.ndarray, method: str) -> np.ndarray:
    arr = np.asarray(path, dtype=np.float64)
    if method == "zpe":
        delta = np.diff(arr, axis=0)
        angles = np.arctan2(delta[:, 1], delta[:, 0])
        direction = np.floor(((angles + np.pi) / (2.0 * np.pi)) * 8.0).astype(np.int64) % 8
        hist = np.bincount(direction, minlength=8).astype(np.float64)
        return hist / np.sum(hist)

    if method == "naive":
        # Intentionally global and coarse: this is naive binning baseline.
        x_bins = np.linspace(-2.0, 2.0, 9)
        y_bins = np.linspace(-2.0, 2.0, 9)
        x = np.digitize(arr[:, 0], x_bins[1:-1], right=False)
        y = np.digitize(arr[:, 1], y_bins[1:-1], right=False)
        joint = x * 8 + y
        hist = np.bincount(joint, minlength=64).astype(np.float64)
        return hist / np.sum(hist)

    if method == "dct":
        x = arr[:, 0]
        y = arr[:, 1]
        fx = np.fft.rfft(x)
        fy = np.fft.rfft(y)
        keep = 10
        feat = np.concatenate(
            [
                fx.real[:keep],
                fx.imag[:keep],
                fy.real[:keep],
                fy.imag[:keep],
            ]
        ).astype(np.float64)
        norm = np.linalg.norm(feat)
        return feat / max(norm, 1e-12)

    raise ValueError(f"unknown method: {method}")


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom <= 1e-12:
        return 0.0
    return float(np.dot(a, b) / denom)
