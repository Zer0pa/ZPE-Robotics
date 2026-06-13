# Falsification Memo

Final verdict: `audit_only_no_algorithmic_edge`.

This gate tested whether a function-aware feature set built from gripper timing, eef/object relations, correction signatures, and local data-quality proxies could beat required baselines on real RoboMimic MH/MG data.

Reward values were withheld from classifier input to avoid outcome leakage. Paired Can was diagnostic only.

## Target Results

- mg_can_outcome_success_vs_failure: primary balanced accuracy 0.9220; best baseline `raw_phase_aligned` 0.9215; margin 0.0006.
- mg_lift_outcome_success_vs_failure: primary balanced accuracy 0.9708; best baseline `fft_lowpass` 0.9708; margin 0.0000.
- mh_can_quality_worse_vs_better: primary balanced accuracy 0.8500; best baseline `pca_global` 1.0000; margin -0.1500.
- mh_lift_quality_worse_vs_better: primary balanced accuracy 0.9500; best baseline `dct_lowpass` 1.0000; margin -0.0500.
- mh_square_quality_worse_vs_better: primary balanced accuracy 0.9000; best baseline `fft_lowpass` 0.9500; margin -0.0500.

## Falsifiers

- Product pass is rejected if wins are only audit, only Paired Can, or only trajectory shape.
- Product pass is rejected if raw, DCT/FFT/PCA, event-only, DemInf-style, or S2I-style baselines explain the signal.
- Nature framing remains a design trigger only; no nature claim is allowed from this gate.
