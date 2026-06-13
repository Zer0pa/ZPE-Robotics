# Falsification Memo

## Verdict

`narrow_retrieval_curation_only`

Sovereign gate pass: `False`.
README claim upgrade allowed: `False`.
Policy-transfer claim allowed: `False`.

## Decisive Comparisons

- Best schema-selected demo RMSE: `0.24157074172517906`
- Best non-schema demo selector: `raw_all_train_mean` with RMSE `0.23555981104874366`
- Schema-selection relative improvement: `-0.025517640932355742`
- ZPE action-adaptation RMSE: `0.26065511041473355`
- Best action-adaptation baseline: `mean_linear_endpoint` with RMSE `0.26065511041473355`
- ZPE action-adaptation relative improvement: `0.0`

## Decision

No positive downstream imitation/adaptation lift survives the frozen baselines. The remaining honest surface is retrieval, curation, and auditability.
