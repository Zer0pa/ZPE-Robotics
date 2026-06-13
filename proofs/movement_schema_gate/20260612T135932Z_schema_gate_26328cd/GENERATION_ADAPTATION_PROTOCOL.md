# Generation / Adaptation Protocol

Status: frozen before final verdict.

## Purpose

Resolve the Phase 3 external movement-primitive blocker by running generation/adaptation-capable baselines rather than retrieval-only coefficient wrappers.

## Feature Surface

Primary features:

- `obs/robot0_eef_pos:0`
- `obs/robot0_eef_pos:1`
- `obs/robot0_eef_pos:2`
- `obs/robot0_gripper_qpos:0`
- `obs/robot0_gripper_qpos:1`

## Models

- `zpe_schema_initializer`: `MovementSchemaV1` relative central form adapted to the held-out start and goal.
- `mean_linear_endpoint`: action mean trajectory with linear start/goal correction.
- `medoid_demo_linear_endpoint`: selected training medoid with linear start/goal correction.
- `fmp_fourier_generation_local`: local Fourier movement primitive generation baseline.
- `external_dmp`: `movement_primitives` DMP with start/goal configuration.
- `external_promp`: `movement_primitives` ProMP with endpoint conditioning.

## Metrics

The authority metric is true-label generation/adaptation error, not retrieval accuracy. Assignment accuracy from generation error is secondary.
