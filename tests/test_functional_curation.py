from __future__ import annotations

import numpy as np

from zpe_robotics.functional_curation import (
    FunctionalDemo,
    build_feature_bank,
    final_functional_verdict,
)


def _demo(demo_id: str, rewards: np.ndarray) -> FunctionalDemo:
    length = 16
    t = np.linspace(0.0, 1.0, length)
    arrays = {
        "actions": np.stack([np.sin(t), np.cos(t), t, -t, t * 0.0, t * 0.1, t * -0.1], axis=1),
        "eef": np.stack([t, t**2, np.sin(t)], axis=1),
        "gripper": np.stack([0.05 - 0.02 * t, -0.05 + 0.02 * t], axis=1),
        "gripper_vel": np.stack([-0.02 + t * 0.0, 0.02 + t * 0.0], axis=1),
        "object": np.stack([0.5 * t, 0.1 + t, 0.2 - t, t, t * 0.0, t * 0.0], axis=1),
        "rewards": rewards.astype(np.float64),
        "dones": np.zeros(length, dtype=np.float64),
    }
    return FunctionalDemo(
        demo_id=demo_id,
        task="can",
        family="mg",
        episode_id=demo_id.rsplit("/", maxsplit=1)[-1],
        source_path="/tmp/fixture.hdf5",
        split="train",
        label_kind="outcome",
        label="success",
        label_rank=1,
        reward_sum=float(np.sum(rewards)),
        final_reward=float(rewards[-1]),
        reward_onset=None,
        arrays=arrays,
    )


def test_functional_vectors_do_not_use_reward_values() -> None:
    zero_reward = np.zeros(16, dtype=np.float64)
    sparse_reward = np.zeros(16, dtype=np.float64)
    sparse_reward[-1] = 1.0
    bank = build_feature_bank(
        [
            _demo("mg/can/demo_1", zero_reward),
            _demo("mg/can/demo_2", sparse_reward),
        ],
        frame_count=16,
    )

    for name, matrix in bank["methods"].items():
        assert np.allclose(matrix[0], matrix[1]), name


def test_final_verdict_rejects_single_target_complement_without_support() -> None:
    verdict = final_functional_verdict(
        {
            "success_criteria": {
                "beats_or_complements_two_real_functional_targets": False,
                "better_outlier_detection_than_baselines": False,
                "better_representative_selection_than_baselines": False,
                "better_functional_diversity_than_baselines": False,
            },
            "target_results": {
                "mg_lift_outcome_success_vs_failure": {
                    "best_baseline_method": "fft_lowpass",
                }
            },
        }
    )

    assert verdict["status"] == "abandon_functional_curation"
    assert verdict["product_worthy"] is False
    assert verdict["readme_claim_upgrade_allowed"] is False
