from __future__ import annotations

from zpe_robotics.anomaly import evaluate_anomaly_detector


def test_anomaly_detector_recall_gate(tmp_path) -> None:
    report = evaluate_anomaly_detector(tmp_path)

    assert report["status"] == "PASS"
    assert report["recall"] >= 0.9
