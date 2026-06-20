"""Metrics for movement-schema gates."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np


def rmse(reference: np.ndarray, candidate: np.ndarray) -> float:
    ref = np.asarray(reference, dtype=np.float64)
    cand = np.asarray(candidate, dtype=np.float64)
    if ref.shape != cand.shape:
        raise ValueError("shape mismatch")
    return float(np.sqrt(np.mean(np.square(ref - cand))))


def velocity_rmse(reference: np.ndarray, candidate: np.ndarray) -> float:
    ref_v = np.gradient(np.asarray(reference, dtype=np.float64), axis=0)
    cand_v = np.gradient(np.asarray(candidate, dtype=np.float64), axis=0)
    return rmse(ref_v, cand_v)


def acceleration_rmse(reference: np.ndarray, candidate: np.ndarray) -> float:
    ref_a = np.gradient(np.gradient(np.asarray(reference, dtype=np.float64), axis=0), axis=0)
    cand_a = np.gradient(np.gradient(np.asarray(candidate, dtype=np.float64), axis=0), axis=0)
    return rmse(ref_a, cand_a)


def endpoint_error(reference: np.ndarray, candidate: np.ndarray) -> float:
    ref = np.asarray(reference, dtype=np.float64)
    cand = np.asarray(candidate, dtype=np.float64)
    if ref.shape != cand.shape:
        raise ValueError("shape mismatch")
    return float(np.sqrt(np.mean(np.square(ref[-1] - cand[-1]))))


def classification_metrics(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"count": 0, "accuracy": 0.0, "by_label": {}}

    correct = [row for row in rows if row["true_label"] == row["predicted_label"]]
    labels = sorted({str(row["true_label"]) for row in rows})
    by_label = {}
    for label in labels:
        label_rows = [row for row in rows if row["true_label"] == label]
        label_correct = [row for row in label_rows if row["predicted_label"] == label]
        by_label[label] = {
            "count": len(label_rows),
            "accuracy": float(len(label_correct) / max(1, len(label_rows))),
        }
    return {
        "count": len(rows),
        "accuracy": float(len(correct) / len(rows)),
        "by_label": by_label,
    }


def mean_average_precision(rows: Sequence[Mapping[str, Any]]) -> float:
    if not rows:
        return 0.0
    ap_values = []
    for row in rows:
        true_label = row["true_label"]
        ranked = row["ranked_labels"]
        hits = 0
        precision_sum = 0.0
        for rank, label in enumerate(ranked, start=1):
            if label == true_label:
                hits += 1
                precision_sum += hits / rank
        ap_values.append(precision_sum / max(1, hits))
    return float(np.mean(ap_values))


def margin_summary(within: Sequence[float], between: Sequence[float]) -> dict[str, float]:
    within_arr = np.asarray(list(within), dtype=np.float64)
    between_arr = np.asarray(list(between), dtype=np.float64)
    if within_arr.size == 0 or between_arr.size == 0:
        return {
            "within_schema_distance_mean": 0.0,
            "within_schema_distance_std": 0.0,
            "between_schema_distance_mean": 0.0,
            "between_schema_distance_std": 0.0,
            "class_margin": 0.0,
        }
    within_mean = float(np.mean(within_arr))
    between_mean = float(np.mean(between_arr))
    return {
        "within_schema_distance_mean": within_mean,
        "within_schema_distance_std": float(np.std(within_arr)),
        "between_schema_distance_mean": between_mean,
        "between_schema_distance_std": float(np.std(between_arr)),
        "class_margin": float(between_mean - within_mean),
    }


def stable_confusion_matrix(rows: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, int]]:
    labels = sorted({str(row["true_label"]) for row in rows} | {str(row["predicted_label"]) for row in rows})
    matrix = {label: {predicted: 0 for predicted in labels} for label in labels}
    for row in rows:
        matrix[str(row["true_label"])][str(row["predicted_label"])] += 1
    return matrix


def utility_per_byte(utility: float, byte_count: int) -> float:
    if byte_count <= 0:
        raise ValueError("byte_count must be positive")
    return float(utility / byte_count)


def description_score(
    schema_bytes: int,
    residual_bytes: int,
    heldout_error: float,
    utility_lift: float,
    lambda_error: float,
    lambda_utility: float,
) -> float:
    """Frozen MDL-surrogate score; lower is better."""
    if schema_bytes < 0 or residual_bytes < 0:
        raise ValueError("byte counts must be non-negative")
    if lambda_error < 0.0 or lambda_utility < 0.0:
        raise ValueError("description-score weights must be non-negative")
    return float(schema_bytes + residual_bytes + lambda_error * heldout_error - lambda_utility * utility_lift)
