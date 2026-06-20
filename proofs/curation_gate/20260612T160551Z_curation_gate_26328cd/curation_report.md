# Curation Gate Report

## Verdict

- Final verdict: `audit_only_narrow_pass`
- Product-worthy narrow scope: `False`
- Broad movement-memory claim allowed: `False`
- README claim upgrade allowed: `False`

## Criteria

- Search beats raw/FFT/DCT/PCA baselines: `False`
- Representative selection beats random/mean/medoid: `False`
- Outlier detection beats distance/LOF/isolation-like baselines: `False`
- Audit receipts expose per-demo reasons and memory costs: `True`

## Baseline Comparison

- Search zpe mAP: `0.9992605158730159`
- Search best baseline: `dct_lowpass` at `0.9973571428571429`
- Representative zpe distance: `0.737441770861501`
- Representative best random/mean/medoid: `mean_central` at `0.6521688242478478`
- Outlier zpe AP: `0.24214199147967957`
- Outlier best baseline: `isolation_projection` at `0.2995772337398062`
