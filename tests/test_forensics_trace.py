from __future__ import annotations

import numpy as np

from zpe_robotics.forensics_trace import (
    EvidenceWindow,
    beats_method,
    final_forensics_pilot_verdict,
    robust_z,
    window_from_scores,
)


def test_window_from_scores_centers_on_peak_with_fixed_fraction() -> None:
    scores = np.zeros(20)
    scores[12] = 10.0

    window = window_from_scores("method", scores, frame_count=20, fraction=0.25)

    assert window.start <= 12 <= window.end
    assert window.end - window.start + 1 == 5
    assert window.fraction == 0.25


def test_evidence_window_reports_target_coverage() -> None:
    window = EvidenceWindow(method="m", start=10, end=20, center=15, frame_count=100, score_peak=1.0)

    assert window.covers(10)
    assert window.covers(20)
    assert not window.covers(21)
    assert not window.covers(None)


def test_pilot_verdict_rejects_baseline_ties() -> None:
    comparison = {
        "success_criteria": {
            "both_tasks_coverage_at_least_0_80": True,
            "both_tasks_window_fraction_at_most_0_25": True,
            "beats_best_non_full_baseline_on_both_tasks": False,
        }
    }

    verdict = final_forensics_pilot_verdict(comparison)

    assert verdict["terminal_verdict"] == "pilot_abandon_forensics_trace"
    assert verdict["product_worthy"] is False
    assert verdict["readme_claim_upgrade_allowed"] is False


def test_beats_method_requires_strict_coverage_or_large_error_reduction() -> None:
    primary = {"keyframe_coverage": 0.75, "median_mean_abs_frame_error": 8.0}
    baseline = {"keyframe_coverage": 0.75, "median_mean_abs_frame_error": 10.0}

    assert beats_method(primary, baseline) is False

    primary["median_mean_abs_frame_error"] = 7.9
    assert beats_method(primary, baseline) is True


def test_robust_z_returns_zero_for_constant_signal() -> None:
    values = robust_z(np.ones(8))

    assert np.allclose(values, 0.0)
