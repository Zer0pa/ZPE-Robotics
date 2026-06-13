from __future__ import annotations

import numpy as np

from zpe_robotics.schema import MovementSchemaV1, SchemaMetadata
from zpe_robotics.schema_adaptation import adapt_endpoint_linear, primitive_feature_indices
from zpe_robotics.schema_baselines import make_standard_baselines
from zpe_robotics.schema_downstream import action_feature_indices, evaluate_demo_selection, select_schema_central
from zpe_robotics.schema_eval import _select_representatives
from zpe_robotics.schema_metrics import description_score, utility_per_byte


def _demo_group(seed: int, offset: float, count: int = 8) -> list[np.ndarray]:
    rng = np.random.default_rng(seed)
    demos = []
    t = np.linspace(0.0, 1.0, 64)
    for _ in range(count):
        phase = rng.normal(0.0, 0.02)
        x = np.sin(2.0 * np.pi * (t + phase)) + offset * np.sin(4.0 * np.pi * t)
        y = np.cos(2.0 * np.pi * (t + phase)) * (0.5 + offset)
        grip = np.tanh((t - 0.5 - offset * 0.1) * 8.0)
        noise = rng.normal(0.0, 0.01, size=(len(t), 3))
        demos.append(np.stack([x, y, grip], axis=1) + noise)
    return demos


def test_movement_schema_fits_multiple_demos_and_scores_heldout() -> None:
    left = _demo_group(seed=11, offset=0.0)
    right = _demo_group(seed=12, offset=0.7)
    left_schema = MovementSchemaV1.fit(left[:6], SchemaMetadata("left", feature_names=("x", "y", "grip")))
    right_schema = MovementSchemaV1.fit(right[:6], SchemaMetadata("right", feature_names=("x", "y", "grip")))

    assert left_schema.demo_count == 6
    assert left_schema.components.shape[0] >= 1
    assert left_schema.score_demo(left[6]).distance < right_schema.score_demo(left[6]).distance
    assert right_schema.score_demo(right[6]).distance < left_schema.score_demo(right[6]).distance


def test_schema_packet_round_trip_preserves_score() -> None:
    demos = _demo_group(seed=21, offset=0.0)
    schema = MovementSchemaV1.fit(demos[:6], SchemaMetadata("move", feature_names=("x", "y", "grip")))
    restored = MovementSchemaV1.from_packet(schema.to_packet())

    assert restored.metadata.action_label == "move"
    assert restored.score_demo(demos[6]).distance == schema.score_demo(demos[6]).distance


def test_standard_baselines_predict_separable_groups() -> None:
    grouped = {
        "left": _demo_group(seed=31, offset=0.0),
        "right": _demo_group(seed=32, offset=0.7),
    }

    for baseline in make_standard_baselines():
        baseline.fit({label: demos[:6] for label, demos in grouped.items()})
        assert baseline.predict(grouped["left"][6]) == "left"
        assert baseline.predict(grouped["right"][6]) == "right"


def test_description_score_and_utility_per_byte_are_frozen_arithmetic() -> None:
    assert utility_per_byte(0.5, 100) == 0.005
    assert description_score(
        schema_bytes=1000,
        residual_bytes=50,
        heldout_error=0.25,
        utility_lift=0.1,
        lambda_error=100.0,
        lambda_utility=1000.0,
    ) == 975.0


def test_select_representatives_starts_with_medoid_then_spreads() -> None:
    rows = [
        {"local_index": 0, "vector": np.array([0.0, 0.0])},
        {"local_index": 1, "vector": np.array([0.1, 0.0])},
        {"local_index": 2, "vector": np.array([10.0, 0.0])},
    ]

    selected = _select_representatives(rows, 2)

    assert [row["local_index"] for row in selected] == [1, 2]


def test_endpoint_adaptation_hits_requested_start_and_goal() -> None:
    base = np.stack([np.linspace(0.0, 1.0, 16), np.linspace(1.0, 2.0, 16)], axis=1)
    adapted = adapt_endpoint_linear(base, np.array([10.0, 20.0]), np.array([12.0, 18.0]))

    assert np.allclose(adapted[0], [10.0, 20.0])
    assert np.allclose(adapted[-1], [12.0, 18.0])


def test_primitive_feature_indices_prefers_eef_and_gripper() -> None:
    names = (
        "obs/robot0_eef_pos:0",
        "obs/robot0_eef_pos:1",
        "obs/robot0_eef_quat:0",
        "obs/robot0_gripper_qpos:0",
        "actions:0",
    )

    assert primitive_feature_indices(names) == (0, 1, 3)


def test_action_feature_indices_requires_action_columns() -> None:
    names = ("obs/robot0_eef_pos:0", "actions:0", "actions:1")

    assert action_feature_indices(names) == (1, 2)


def test_schema_selected_demos_feed_downstream_action_eval() -> None:
    grouped = {
        "left": _demo_group(seed=41, offset=0.0, count=8),
        "right": _demo_group(seed=42, offset=0.7, count=8),
    }
    feature_names = ("obs/robot0_eef_pos:0", "actions:0", "actions:1")
    schemas = {
        label: MovementSchemaV1.fit(demos[:6], SchemaMetadata(label, feature_names=feature_names))
        for label, demos in grouped.items()
    }
    selected = select_schema_central({label: demos[:6] for label, demos in grouped.items()}, schemas, budget=2)
    test_items = [
        ("left", "demo_6", grouped["left"][6]),
        ("right", "demo_6", grouped["right"][6]),
    ]

    result = evaluate_demo_selection(
        "schema_selected",
        {label: demos[:6] for label, demos in grouped.items()},
        test_items,
        selected,
        feature_indices=(1, 2),
        frame_count=128,
        selector_overhead_bytes=100,
        budget=2,
    )

    assert result.selected_demo_count == 4
    assert result.model_zlib_bytes > 100
    assert result.action_rmse_mean >= 0.0
