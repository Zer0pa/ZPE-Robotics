"""Trajectory anomaly injection and detection utilities."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .codec import ZPBotCodec
from .fixtures import generate_joint_trajectory, inject_discontinuities
from .vla_bridge import trajectory_to_fast_tokens
from .wire import decode_packet


@dataclass(frozen=True)
class AnomalyReport:
    filepath: str
    score: float
    flagged: bool
    threshold: float


class AnomalyDetector:
    """Fleet-level anomaly detector over per-joint FAST-token histograms."""

    def __init__(self, *, z_threshold: float = 3.0) -> None:
        self.z_threshold = float(z_threshold)
        self._mean: np.ndarray | None = None
        self._std: np.ndarray | None = None

    def fit(self, filepaths: list[str | Path]) -> AnomalyDetector:
        if not filepaths:
            raise ValueError("fit expects at least one trajectory file")
        rows = np.stack([_file_token_histogram(path) for path in filepaths], axis=0)
        self._mean = np.mean(rows, axis=0)
        self._std = np.std(rows, axis=0)
        self._std = np.where(self._std < 1.0e-6, 1.0e-6, self._std)
        return self

    def score(self, filepath: str | Path) -> float:
        if self._mean is None or self._std is None:
            raise ValueError("detector must be fit before scoring")
        hist = _file_token_histogram(filepath)
        z = np.abs((hist - self._mean) / self._std)
        return float((np.linalg.norm(z) / np.sqrt(z.size)) * 3.0)

    def classify(self, filepath: str | Path) -> AnomalyReport:
        score = self.score(filepath)
        return AnomalyReport(
            filepath=str(filepath),
            score=score,
            flagged=bool(score > self.z_threshold),
            threshold=self.z_threshold,
        )


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


def evaluate_anomaly_detector(output_dir: str | Path, *, seed: int = 20260243) -> dict[str, float | int | str]:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    codec = ZPBotCodec(keep_coeffs=8)

    nominal_paths: list[Path] = []
    anomalous_paths: list[Path] = []

    for idx in range(20):
        trajectory = generate_joint_trajectory(num_frames=4096, num_joints=6, seed=seed + idx)
        path = root / f"nominal_{idx:02d}.zpbot"
        path.write_bytes(codec.encode(trajectory))
        nominal_paths.append(path)

    for idx in range(5):
        base = generate_joint_trajectory(num_frames=4096, num_joints=6, seed=seed + 100 + idx)
        anomaly = inject_discontinuities(base, seed=seed + 200 + idx, spike_count=18, magnitude=1.4)
        anomaly[1024:3072, 0] += 1.6
        anomaly[:, 1] *= -1.0
        anomaly[:, 2] += np.linspace(0.0, 2.0, anomaly.shape[0])
        path = root / f"anomalous_{idx:02d}.zpbot"
        path.write_bytes(codec.encode(anomaly))
        anomalous_paths.append(path)

    detector = AnomalyDetector(z_threshold=3.0).fit(nominal_paths)
    flagged = [detector.classify(path).flagged for path in anomalous_paths]
    recall = float(sum(flagged) / max(1, len(flagged)))
    return {
        "status": "PASS" if recall >= 0.9 else "FAIL",
        "recall": recall,
        "threshold": detector.z_threshold,
        "nominal_count": len(nominal_paths),
        "anomalous_count": len(anomalous_paths),
    }


def _file_token_histogram(filepath: str | Path) -> np.ndarray:
    trajectory = decode_packet(Path(filepath).read_bytes())
    return _trajectory_token_histogram(trajectory)


def _trajectory_token_histogram(trajectory: np.ndarray) -> np.ndarray:
    tokens = trajectory_to_fast_tokens(trajectory)
    features: list[np.ndarray] = []
    for joint_idx in range(tokens.shape[1]):
        hist = np.bincount(tokens[:, joint_idx].astype(np.int64), minlength=24).astype(np.float64)
        denom = float(np.sum(hist))
        if denom <= 0.0:
            raise ValueError("token histogram denominator is zero")
        features.append(hist / denom)
    return np.concatenate(features, axis=0)
