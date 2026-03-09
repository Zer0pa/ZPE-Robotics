"""Trajectory anomaly injection and detection utilities."""

from __future__ import annotations

import numpy as np


def inject_faults(
    trajectory: np.ndarray,
    seed: int,
    spike_rate: float = 0.015,
    spike_magnitude: float = 2.0,
) -> tuple[np.ndarray, np.ndarray]:
    arr = np.asarray(trajectory, dtype=np.float64)
    if arr.ndim != 2:
        raise ValueError("trajectory must be 2D")
    frames, joints = arr.shape
    rng = np.random.default_rng(seed)

    faulted = np.array(arr, copy=True)
    truth = np.zeros(frames, dtype=bool)

    spike_count = max(1, int(frames * spike_rate))
    idxs = rng.choice(np.arange(3, frames - 3), size=spike_count, replace=False)
    joint_idxs = rng.choice(np.arange(joints), size=spike_count, replace=True)

    for idx, j in zip(idxs, joint_idxs, strict=True):
        sign = 1.0 if rng.uniform() > 0.5 else -1.0
        faulted[idx, j] += sign * spike_magnitude
        truth[idx] = True

    for _ in range(3):
        start = int(rng.integers(low=64, high=max(65, frames - 128)))
        duration = int(rng.integers(low=12, high=30))
        end = min(frames, start + duration)
        joint = int(rng.integers(0, joints))
        faulted[start:end, joint] = faulted[start - 1, joint]
        truth[start:end] = True

    return faulted, truth


def detect_anomalies(trajectory: np.ndarray, z_threshold: float = 3.5) -> np.ndarray:
    arr = np.asarray(trajectory, dtype=np.float64)
    if arr.ndim != 2:
        raise ValueError("trajectory must be 2D")

    velocity = np.diff(arr, axis=0, prepend=arr[:1, :])
    accel = np.diff(velocity, axis=0, prepend=velocity[:1, :])
    mag = np.abs(accel)

    mean = np.mean(mag, axis=0)
    std = np.std(mag, axis=0)
    std = np.where(std < 1e-9, 1e-9, std)

    z = (mag - mean[None, :]) / std[None, :]
    score = np.max(z, axis=1)
    spike_flags = score > z_threshold

    # Detect injected frozen segments (flatlined joint deltas) via run-length checks.
    stuck_flags = np.zeros(arr.shape[0], dtype=bool)
    for joint in range(arr.shape[1]):
        near_zero = np.abs(velocity[:, joint]) < 1.0e-14
        i = 0
        while i < near_zero.size:
            if near_zero[i]:
                start = i
                while i < near_zero.size and near_zero[i]:
                    i += 1
                if (i - start) >= 5:
                    stuck_flags[start:i] = True
            else:
                i += 1

    return spike_flags | stuck_flags


def precision_recall(truth: np.ndarray, pred: np.ndarray) -> tuple[float, float]:
    truth_bool = np.asarray(truth, dtype=bool)
    pred_bool = np.asarray(pred, dtype=bool)
    if truth_bool.shape != pred_bool.shape:
        raise ValueError("truth/pred shape mismatch")

    tp = float(np.sum(truth_bool & pred_bool))
    fp = float(np.sum(~truth_bool & pred_bool))
    fn = float(np.sum(truth_bool & ~pred_bool))

    precision = tp / max(1.0, tp + fp)
    recall = tp / max(1.0, tp + fn)
    return precision, recall
