"""Deterministic fixture generation for Wave-1 robotics benchmarks."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class FixtureBundle:
    arm_nominal: np.ndarray
    arm_adversarial: np.ndarray
    humanoid_nominal: np.ndarray
    humanoid_adversarial: np.ndarray


def build_fixture_bundle(seed: int) -> FixtureBundle:
    arm_nominal = generate_joint_trajectory(num_frames=4096, num_joints=6, seed=seed + 1)
    humanoid_nominal = generate_joint_trajectory(num_frames=4096, num_joints=32, seed=seed + 2)
    arm_adversarial = inject_discontinuities(arm_nominal, seed=seed + 3, spike_count=18, magnitude=1.2)
    humanoid_adversarial = inject_discontinuities(humanoid_nominal, seed=seed + 4, spike_count=26, magnitude=1.4)
    return FixtureBundle(
        arm_nominal=arm_nominal,
        arm_adversarial=arm_adversarial,
        humanoid_nominal=humanoid_nominal,
        humanoid_adversarial=humanoid_adversarial,
    )


def generate_joint_trajectory(num_frames: int, num_joints: int, seed: int) -> np.ndarray:
    if num_frames < 8:
        raise ValueError("num_frames must be >= 8")
    if num_joints < 1:
        raise ValueError("num_joints must be >= 1")

    rng = np.random.default_rng(seed)
    t = np.linspace(0.0, 2.0 * np.pi, num_frames, endpoint=False)
    signal = np.zeros((num_frames, num_joints), dtype=np.float64)

    for j in range(num_joints):
        component_count = 3 + (j % 2)
        joint = np.zeros(num_frames, dtype=np.float64)
        for k in range(1, component_count + 1):
            amp = rng.uniform(0.2, 1.0) / (k ** 1.3)
            phase = rng.uniform(0.0, 2.0 * np.pi)
            freq = float(k)
            joint += amp * np.sin(freq * t + phase)
        # Integer-frequency harmonics preserve strict spectral sparsity and determinism.
        joint += 0.08 * np.cos((1 + (j % 3)) * t + rng.uniform(0.0, 2.0 * np.pi))
        joint += rng.normal(0.0, 1.0e-8, size=num_frames)
        signal[:, j] = np.clip(joint, -2.8, 2.8)

    return signal


def inject_discontinuities(
    trajectory: np.ndarray,
    seed: int,
    spike_count: int,
    magnitude: float,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    out = np.array(trajectory, dtype=np.float64, copy=True)
    frames, joints = out.shape

    frame_idx = rng.choice(np.arange(2, frames - 2), size=spike_count, replace=False)
    joint_idx = rng.choice(np.arange(joints), size=spike_count, replace=True)

    for f, j in zip(frame_idx, joint_idx, strict=True):
        direction = 1.0 if rng.uniform() > 0.5 else -1.0
        out[f, j] += direction * magnitude

    segment_start = int(rng.integers(low=128, high=max(129, frames - 512)))
    segment_len = int(rng.integers(low=32, high=96))
    segment_end = min(frames, segment_start + segment_len)
    out[segment_start:segment_end, :] += rng.normal(0.0, magnitude * 0.07, size=(segment_end - segment_start, joints))

    return np.clip(out, -3.1, 3.1)


def malformed_trajectory_inputs() -> list[np.ndarray]:
    return [
        np.array([1.0, 2.0, 3.0], dtype=np.float64),
        np.array([[1.0, np.nan], [2.0, 3.0]], dtype=np.float64),
        np.array([[1.0, np.inf], [2.0, 3.0]], dtype=np.float64),
        np.empty((0, 4), dtype=np.float64),
    ]


def make_rosbag_fixture(trajectory: np.ndarray, seed: int) -> list[dict[str, object]]:
    rng = np.random.default_rng(seed)
    records: list[dict[str, object]] = []
    for idx in range(12):
        start = idx * 256
        end = start + 256
        window = trajectory[start:end, :]
        records.append(
            {
                "index": idx,
                "topic": "/joint_states",
                "timestamp_ns": int(1_700_000_000_000_000_000 + idx * 5_000_000),
                "robot": "wave1_arm",
                "joint_names": [f"joint_{j}" for j in range(window.shape[1])],
                "trajectory": window,
                "quality": float(rng.uniform(0.98, 1.0)),
            }
        )
    return records
