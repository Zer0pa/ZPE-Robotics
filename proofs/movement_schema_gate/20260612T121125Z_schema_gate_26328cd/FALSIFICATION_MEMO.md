# Falsification Memo

## Verdict

`retrieval_slice_pass_sovereign_incomplete`

Sovereign gate pass: `False`.
README claim upgrade allowed: `False`.

## Primary Evidence

- schema accuracy: `1.0`
- best local baseline accuracy: `1.0`
- Can margin mean: `0.2181864411825071`
- Can margin min: `0.1150886247215413`

## Baseline Pressure

Local baseline accuracies:

```json
{
  "dct_lowpass": 0.995,
  "dmp_rbf_weights": 0.72,
  "fft_lowpass": 0.99,
  "fmp_fourier_weights": 0.92,
  "global_pca": 0.99,
  "mean_trajectory": 0.985,
  "nearest_demo": 1.0,
  "promp_rbf_weights": 0.715
}
```

## Failure / Narrowing Notes

- Full DMP, ProMP, and FMP generation/adaptation behavior is not proven by this run.
- Policy transfer is not attempted.
- Branch-removal natural-primitive ablations are proxy-level only.
- The old `.zpbot` codec remains single-trajectory spectral truncation and is not relabeled as the schema learner.

## Decision

Continue only on the narrow retrieval/demo-selection wedge unless a follow-up gate beats serious movement-primitive baselines on generation, adaptation, or policy-facing transfer.
