# Functional Curation Report

Verdict: `audit_only_no_algorithmic_edge`.

The tested mechanism used function-oriented features rather than trajectory-shape retrieval: phase/event timing, object/eef relations, gripper events, correction signatures, and local action-divergence/transition-diversity proxies.

## Baseline Result

- mg_can_outcome_success_vs_failure: fail; primary=0.9220, best_baseline=raw_phase_aligned:0.9215.
- mg_lift_outcome_success_vs_failure: fail; primary=0.9708, best_baseline=fft_lowpass:0.9708.
- mh_can_quality_worse_vs_better: fail; primary=0.8500, best_baseline=pca_global:1.0000.
- mh_lift_quality_worse_vs_better: fail; primary=0.9500, best_baseline=dct_lowpass:1.0000.
- mh_square_quality_worse_vs_better: fail; primary=0.9000, best_baseline=fft_lowpass:0.9500.
