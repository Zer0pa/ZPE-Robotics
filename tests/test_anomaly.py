from __future__ import annotations

from zpe_robotics.anomaly import (
    ANOMALY_BASELINE_Z_THRESHOLD,
    ANOMALY_FALSE_POSITIVE_RATE_CEILING,
    ANOMALY_RECALL_FLOOR,
    DEFAULT_ANOMALY_Z_THRESHOLD,
    choose_anomaly_threshold,
    evaluate_anomaly_detector,
    sweep_anomaly_thresholds,
)


def test_anomaly_detector_meets_false_positive_and_recall_gates(tmp_path) -> None:
    report = evaluate_anomaly_detector(tmp_path)

    assert report["status"] == "PASS"
    assert report["false_positive_rate"] <= ANOMALY_FALSE_POSITIVE_RATE_CEILING
    assert report["recall"] >= ANOMALY_RECALL_FLOOR
    assert report["threshold"] == DEFAULT_ANOMALY_Z_THRESHOLD


def test_anomaly_threshold_sweep_preserves_phase9_baseline_and_selects_threshold(tmp_path) -> None:
    sweep = sweep_anomaly_thresholds(tmp_path)

    baseline = next(result for result in sweep["threshold_grid"] if result["threshold"] == ANOMALY_BASELINE_Z_THRESHOLD)

    assert sweep["status"] == "PASS"
    assert sweep["selected_threshold"] == DEFAULT_ANOMALY_Z_THRESHOLD
    assert sweep["selected_result"]["threshold"] == DEFAULT_ANOMALY_Z_THRESHOLD
    assert baseline["false_positive_rate"] > ANOMALY_FALSE_POSITIVE_RATE_CEILING
    assert baseline["recall"] >= ANOMALY_RECALL_FLOOR
    assert sweep["selected_result"]["false_positive_rate"] <= ANOMALY_FALSE_POSITIVE_RATE_CEILING
    assert sweep["selected_result"]["recall"] >= ANOMALY_RECALL_FLOOR


def test_choose_anomaly_threshold_returns_first_valid_result() -> None:
    results = [
        {"threshold": 3.0, "false_positive_rate": 0.2, "recall": 1.0},
        {"threshold": 3.25, "false_positive_rate": 0.0, "recall": 1.0},
        {"threshold": 3.5, "false_positive_rate": 0.0, "recall": 1.0},
    ]

    chosen = choose_anomaly_threshold(results)

    assert chosen == results[1]
