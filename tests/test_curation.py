from __future__ import annotations

import json

import numpy as np

from zpe_robotics.schema import DemoMetadata
from zpe_robotics.schema_curation import (
    curate_movement_dataset,
    detect_outliers_from_manifest,
    search_movement_index,
    select_representatives_from_manifest,
)
from zpe_robotics.schema_eval import MovementDemo, freeze_splits


def _curation_demos() -> list[MovementDemo]:
    rng = np.random.default_rng(91)
    demos: list[MovementDemo] = []
    feature_fields = (
        "obs/robot0_eef_pos",
        "obs/robot0_gripper_qpos",
        "actions",
    )
    for label, offset in (("left", 0.0), ("right", 0.8)):
        for idx in range(12):
            t = np.linspace(0.0, 1.0, 48)
            phase = rng.normal(0.0, 0.01)
            x = np.sin(2.0 * np.pi * (t + phase)) + offset
            y = np.cos(2.0 * np.pi * (t + phase)) * (0.5 + offset)
            grip = np.tanh((t - 0.5) * 8.0)
            act0 = np.gradient(x)
            act1 = np.gradient(y)
            noise = rng.normal(0.0, 0.01, size=(len(t), 5))
            trajectory = np.stack([x, y, grip, act0, act1], axis=1) + noise
            metadata = DemoMetadata(
                action_label=label,
                episode_id=f"demo_{idx}",
                source_path=f"/tmp/{label}.hdf5",
                feature_fields=feature_fields,
            )
            demos.append(MovementDemo(trajectory=trajectory, metadata=metadata, frame_count=trajectory.shape[0]))
    return demos


def _manifest() -> dict[str, object]:
    return {
        "schema_version": 1,
        "dataset_family": "fixture",
        "actions": ["left", "right"],
        "feature_names": [
            "obs/robot0_eef_pos:0",
            "obs/robot0_eef_pos:1",
            "obs/robot0_gripper_qpos:0",
            "actions:0",
            "actions:1",
        ],
        "datasets": [],
        "episode_count": 24,
    }


def test_curation_gate_emits_required_artifacts_and_cli_helpers(tmp_path) -> None:
    demos = _curation_demos()
    splits = freeze_splits(demos, seed=20260615)
    verdict = curate_movement_dataset(
        demos,
        _manifest(),
        splits,
        tmp_path,
        frame_count=32,
        component_count=3,
        budget_per_class=2,
    )

    assert verdict["status"] in {
        "curation_product_pass",
        "audit_only_narrow_pass",
        "baseline_tie_no_product_edge",
        "abandon_productization",
    }
    for name in (
        "movement_index.json",
        "representatives.json",
        "outliers.json",
        "curation_audit.json",
        "curation_report.md",
        "search_eval.json",
        "representative_selection_eval.json",
        "outlier_detection_eval.json",
        "baseline_comparison.json",
        "FINAL_GATE_VERDICT.json",
    ):
        assert (tmp_path / name).exists()

    index = json.loads((tmp_path / "movement_index.json").read_text(encoding="utf-8"))
    query_demo = index["entries"][0]["demo_id"]
    result = search_movement_index(tmp_path / "movement_index.json", query_demo, top_k=3)
    assert result["query_demo"] == query_demo
    assert len(result["results"]) == 3

    reps = select_representatives_from_manifest(tmp_path / "DATASET_MANIFEST.json", 2, tmp_path / "reps_cli.json")
    outliers = detect_outliers_from_manifest(tmp_path / "DATASET_MANIFEST.json", tmp_path / "outliers_cli.json")
    assert reps["budget_per_class"] == 2
    assert outliers["silver_positive_count"] > 0
