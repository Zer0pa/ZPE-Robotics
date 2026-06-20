# Baseline Protocol

Status: frozen before final verdict.

## Dataset And Split

- dataset: `robomimic`
- actions: `can, lift, square, transport, tool_hang`
- split policy: `same frozen split as schema and baseline evaluation`

## Exemplar-Memory Baselines

- nearest-demo and kNN use `start-relative canonicalized trajectory plus velocity branch`;
- retained-demo budgets per class: `[1, 2, 5, 10, 20, 'all']`;
- representative demos are selected by `per-action medoid first, then deterministic farthest-first representatives`;
- storage includes raw float32 trajectory bytes, zlib-compressed float32 bytes, and metadata bytes.

## Rate-Distortion / MDL

The frozen score is:

`description_score = schema_bytes + residual_bytes + lambda_error * heldout_error - lambda_utility * utility_lift`

with `lambda_error = 100000.0` and `lambda_utility = 1000000.0`.

## Movement-Primitive Baselines

Local DMP/ProMP/FMP coefficient wrappers are kept as retrieval-pressure rows. External generation/adaptation status is `blocked_external_generation_adaptation`. This blocks any movement-primitive adaptation claim in this run.
