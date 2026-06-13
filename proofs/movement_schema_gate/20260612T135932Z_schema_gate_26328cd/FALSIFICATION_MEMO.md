# Falsification Memo

## Verdict

`generation_adaptation_gate_failed_nearest_demo_or_primitives_dominate`

Sovereign gate pass: `False`.
README claim upgrade allowed: `False`.

## Model Metrics

- `zpe_schema_initializer`: rmse `0.03685011709404354`, assignment `0.985`
- `mean_linear_endpoint`: rmse `0.03685011709404354`, assignment `0.985`
- `medoid_demo_linear_endpoint`: rmse `0.04096649096824535`, assignment `0.96`
- `fmp_fourier_generation_local`: rmse `0.04633186566827634`, assignment `0.975`
- `external_dmp`: rmse `0.04130035924127012`, assignment `0.995`
- `external_promp`: rmse `0.06380404089039966`, assignment `0.815`

## Decision

Best baseline: `mean_linear_endpoint`.
ZPE relative improvement versus best baseline: `0.0`.
Blocker-resolution decision: `narrow`.

This is not policy transfer and not live robot execution. Treat support, if any, as a trajectory-level adaptation receipt only.
