"""VLA token export over the frozen wire-v1 utility-kernel surface."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from .constants import AUTHORITY_SURFACE, AUTHORITY_WIRE_COMPATIBILITY
from .primitives import generate_primitive_corpus
from .vla_eval import evaluate_token_quality
from .wire import decode_packet


def trajectory_to_fast_tokens(trajectory: np.ndarray) -> np.ndarray:
    """Convert a joint trajectory into the frozen 24-token FAST-style surface."""

    arr = np.asarray(trajectory, dtype=np.float64)
    if arr.ndim != 2:
        raise ValueError("trajectory must be a 2D array [frames, joints]")
    if arr.shape[0] < 8:
        raise ValueError("trajectory must include at least 8 frames")

    velocity = np.diff(arr, axis=0, prepend=arr[:1, :])
    accel = np.diff(velocity, axis=0, prepend=velocity[:1, :])
    angles = np.arctan2(accel, velocity)
    direction = np.floor(((angles + np.pi) / (2.0 * np.pi)) * 8.0).astype(np.int64) % 8

    magnitude = np.sqrt(np.square(velocity) + np.square(accel))
    q1, q2 = np.quantile(magnitude.reshape(-1), [0.33, 0.66])
    cuts = np.array([float(q1), float(q2)], dtype=np.float64)
    mag_bin = np.digitize(magnitude, cuts, right=False)
    mag_bin = np.clip(mag_bin, 0, 2)

    return (direction * 3 + mag_bin).astype(np.int32)


def export_fast_tokens(zpbot_path: str | Path) -> np.ndarray:
    path = Path(zpbot_path)
    trajectory = decode_packet(path.read_bytes())
    return trajectory_to_fast_tokens(trajectory)


def export_cubicvla_tokens(zpbot_path: str | Path) -> dict[str, Any]:
    tokens = export_fast_tokens(zpbot_path)
    return {
        "authority_surface": AUTHORITY_SURFACE,
        "compatibility_mode": AUTHORITY_WIRE_COMPATIBILITY,
        "tokens": tokens.tolist(),
        "timestamps": list(range(tokens.shape[0])),
        "joint_names": [f"joint_{idx}" for idx in range(tokens.shape[1])],
    }


def evaluate_fast_token_accuracy(seed: int = 20260243) -> dict[str, float]:
    library, queries = generate_primitive_corpus(
        seed=seed,
        library_per_label=60,
        query_per_label=24,
        length=96,
    )
    report = evaluate_token_quality(library + queries)
    raw_accuracy = float(report["zpe_token_accuracy"])
    return {
        "raw_token_accuracy": raw_accuracy,
        "token_accuracy": float(round(raw_accuracy, 3)),
        "naive_binning_accuracy": float(report["naive_binning_accuracy"]),
        "delta_vs_naive": float(report["delta_vs_naive"]),
    }
