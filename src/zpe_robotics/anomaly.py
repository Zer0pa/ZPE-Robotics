"""Trajectory anomaly injection and detection utilities."""

from __future__ import annotations

from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from .codec import ZPBotCodec
from .fixtures import generate_joint_trajectory, inject_discontinuities
from .vla_bridge import trajectory_to_fast_tokens
from .wire import decode_packet

ANOMALY_BASELINE_Z_THRESHOLD = 3.0
DEFAULT_ANOMALY_Z_THRESHOLD = 3.22
ANOMALY_FALSE_POSITIVE_RATE_CEILING = 0.05
ANOMALY_RECALL_FLOOR = 0.9
ANOMALY_TRAINING_NOMINAL_COUNT = 60
ANOMALY_EVALUATION_NOMINAL_COUNT = 100
ANOMALY_EVALUATION_ANOMALOUS_COUNT = 10
ANOMALY_NUM_FRAMES = 4096
ANOMALY_NUM_JOINTS = 6
ANOMALY_CORPUS_IDENTITY = "phase10-file-level-histogram-holdout-v1"
ANOMALY_SWEEP_THRESHOLDS = tuple(round(ANOMALY_BASELINE_Z_THRESHOLD + 0.01 * idx, 2) for idx in range(101))


@dataclass(frozen=True)
class AnomalyReport:
    filepath: str
    score: float
    flagged: bool
    threshold: float


@dataclass(frozen=True)
class AnomalyEvaluationCorpus:
    training_nominal_paths: list[Path]
    nominal_paths: list[Path]
    anomalous_paths: list[Path]
    corpus_identity: str


class AnomalyDetector:
    """Fleet-level anomaly detector over per-joint FAST-token histograms."""

    def __init__(self, *, z_threshold: float = DEFAULT_ANOMALY_Z_THRESHOLD) -> None:
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


def build_anomaly_evaluation_corpus(output_dir: str | Path, *, seed: int = 20260243) -> AnomalyEvaluationCorpus:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    codec = ZPBotCodec(keep_coeffs=8)

    training_nominal_paths: list[Path] = []
    nominal_paths: list[Path] = []
    anomalous_paths: list[Path] = []

    train_root = root / "train_nominal"
    eval_root = root / "eval_nominal"
    anomaly_root = root / "eval_anomalous"
    train_root.mkdir(parents=True, exist_ok=True)
    eval_root.mkdir(parents=True, exist_ok=True)
    anomaly_root.mkdir(parents=True, exist_ok=True)

    for idx in range(ANOMALY_TRAINING_NOMINAL_COUNT):
        trajectory = generate_joint_trajectory(num_frames=ANOMALY_NUM_FRAMES, num_joints=ANOMALY_NUM_JOINTS, seed=seed + idx)
        path = train_root / f"nominal_{idx:03d}.zpbot"
        path.write_bytes(codec.encode(trajectory))
        training_nominal_paths.append(path)

    for idx in range(ANOMALY_EVALUATION_NOMINAL_COUNT):
        trajectory = generate_joint_trajectory(
            num_frames=ANOMALY_NUM_FRAMES,
            num_joints=ANOMALY_NUM_JOINTS,
            seed=seed + 1000 + idx,
        )
        path = eval_root / f"nominal_{idx:03d}.zpbot"
        path.write_bytes(codec.encode(trajectory))
        nominal_paths.append(path)

    for idx in range(ANOMALY_EVALUATION_ANOMALOUS_COUNT):
        base = generate_joint_trajectory(
            num_frames=ANOMALY_NUM_FRAMES,
            num_joints=ANOMALY_NUM_JOINTS,
            seed=seed + 2000 + idx,
        )
        anomaly = inject_discontinuities(base, seed=seed + 3000 + idx, spike_count=18, magnitude=1.4)
        anomaly[1024:3072, 0] += 1.6
        anomaly[:, 1] *= -1.0
        anomaly[:, 2] += np.linspace(0.0, 2.0, anomaly.shape[0])
        path = anomaly_root / f"anomalous_{idx:03d}.zpbot"
        path.write_bytes(codec.encode(anomaly))
        anomalous_paths.append(path)

    return AnomalyEvaluationCorpus(
        training_nominal_paths=training_nominal_paths,
        nominal_paths=nominal_paths,
        anomalous_paths=anomalous_paths,
        corpus_identity=ANOMALY_CORPUS_IDENTITY,
    )


def choose_anomaly_threshold(
    results: list[dict[str, float | int]],
    *,
    false_positive_rate_ceiling: float = ANOMALY_FALSE_POSITIVE_RATE_CEILING,
    recall_floor: float = ANOMALY_RECALL_FLOOR,
) -> dict[str, float | int] | None:
    return next(
        (
            result
            for result in results
            if float(result["false_positive_rate"]) <= false_positive_rate_ceiling
            and float(result["recall"]) >= recall_floor
        ),
        None,
    )


def best_available_anomaly_threshold(
    results: list[dict[str, float | int]],
    *,
    false_positive_rate_ceiling: float = ANOMALY_FALSE_POSITIVE_RATE_CEILING,
    recall_floor: float = ANOMALY_RECALL_FLOOR,
) -> dict[str, float | int]:
    recall_preserving = [result for result in results if float(result["recall"]) >= recall_floor]
    if recall_preserving:
        return min(
            recall_preserving,
            key=lambda result: (
                float(result["false_positive_rate"]) - false_positive_rate_ceiling,
                float(result["threshold"]),
            ),
        )
    return max(results, key=lambda result: (float(result["recall"]), -float(result["false_positive_rate"])))


def _evaluate_scores(
    nominal_scores: list[float],
    anomalous_scores: list[float],
    *,
    threshold: float,
) -> dict[str, float | int]:
    false_positive_count = int(sum(score > threshold for score in nominal_scores))
    true_positive_count = int(sum(score > threshold for score in anomalous_scores))
    false_negative_count = int(len(anomalous_scores) - true_positive_count)
    true_negative_count = int(len(nominal_scores) - false_positive_count)
    return {
        "threshold": float(threshold),
        "false_positive_rate": float(false_positive_count / max(1, len(nominal_scores))),
        "false_positive_count": false_positive_count,
        "recall": float(true_positive_count / max(1, len(anomalous_scores))),
        "true_positive_count": true_positive_count,
        "false_negative_count": false_negative_count,
        "true_negative_count": true_negative_count,
    }


def evaluate_anomaly_detector(
    output_dir: str | Path,
    *,
    seed: int = 20260243,
    threshold: float = DEFAULT_ANOMALY_Z_THRESHOLD,
) -> dict[str, float | int | str]:
    corpus = build_anomaly_evaluation_corpus(output_dir, seed=seed)
    detector = AnomalyDetector(z_threshold=threshold).fit(corpus.training_nominal_paths)
    nominal_scores = [float(detector.score(path)) for path in corpus.nominal_paths]
    anomalous_scores = [float(detector.score(path)) for path in corpus.anomalous_paths]
    evaluation = _evaluate_scores(nominal_scores, anomalous_scores, threshold=detector.z_threshold)

    return {
        "status": (
            "PASS"
            if float(evaluation["false_positive_rate"]) <= ANOMALY_FALSE_POSITIVE_RATE_CEILING
            and float(evaluation["recall"]) >= ANOMALY_RECALL_FLOOR
            else "FAIL"
        ),
        "corpus_identity": corpus.corpus_identity,
        "authority_surface": "zpbot-v2",
        "compatibility_mode": "wire-v1",
        "generation_timestamp": datetime.now(timezone.utc).isoformat(),
        "false_positive_rate": float(evaluation["false_positive_rate"]),
        "false_positive_count": int(evaluation["false_positive_count"]),
        "recall": float(evaluation["recall"]),
        "true_positive_count": int(evaluation["true_positive_count"]),
        "false_negative_count": int(evaluation["false_negative_count"]),
        "true_negative_count": int(evaluation["true_negative_count"]),
        "threshold": detector.z_threshold,
        "training_nominal_count": len(corpus.training_nominal_paths),
        "nominal_count": len(corpus.nominal_paths),
        "anomalous_count": len(corpus.anomalous_paths),
        "target_false_positive_rate": ANOMALY_FALSE_POSITIVE_RATE_CEILING,
        "target_recall": ANOMALY_RECALL_FLOOR,
    }


def sweep_anomaly_thresholds(
    output_dir: str | Path,
    *,
    seed: int = 20260243,
    thresholds: tuple[float, ...] = ANOMALY_SWEEP_THRESHOLDS,
) -> dict[str, Any]:
    corpus = build_anomaly_evaluation_corpus(output_dir, seed=seed)
    detector = AnomalyDetector(z_threshold=ANOMALY_BASELINE_Z_THRESHOLD).fit(corpus.training_nominal_paths)
    nominal_scores = [float(detector.score(path)) for path in corpus.nominal_paths]
    anomalous_scores = [float(detector.score(path)) for path in corpus.anomalous_paths]

    results: list[dict[str, float | int]] = []
    for threshold in thresholds:
        results.append(_evaluate_scores(nominal_scores, anomalous_scores, threshold=threshold))

    selected = choose_anomaly_threshold(results)
    best_available = best_available_anomaly_threshold(results)
    baseline = next(result for result in results if float(result["threshold"]) == ANOMALY_BASELINE_Z_THRESHOLD)

    return {
        "status": "PASS" if selected is not None else "FAIL",
        "corpus_identity": corpus.corpus_identity,
        "authority_surface": "zpbot-v2",
        "compatibility_mode": "wire-v1",
        "generation_timestamp": datetime.now(timezone.utc).isoformat(),
        "baseline_threshold": ANOMALY_BASELINE_Z_THRESHOLD,
        "baseline_result": baseline,
        "selected_threshold": selected["threshold"] if selected is not None else best_available["threshold"],
        "selected_threshold_meets_gate": selected is not None,
        "selected_result": selected,
        "best_available_result": best_available,
        "training_nominal_count": len(corpus.training_nominal_paths),
        "nominal_count": len(corpus.nominal_paths),
        "anomalous_count": len(corpus.anomalous_paths),
        "threshold_grid": results,
        "nominal_score_range": {
            "min": float(min(nominal_scores)),
            "max": float(max(nominal_scores)),
        },
        "anomalous_score_range": {
            "min": float(min(anomalous_scores)),
            "max": float(max(anomalous_scores)),
        },
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
