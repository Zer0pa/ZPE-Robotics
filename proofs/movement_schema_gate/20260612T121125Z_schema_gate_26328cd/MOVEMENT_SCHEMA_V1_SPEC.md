# MovementSchemaV1 Spec

Status: internal proof artifact

## Packet

- schema version: `movement-schema-v1`
- action label: `can`
- frame count: `128`
- component count requested: `8`
- component count fitted: `8`
- demo count: `120`
- split hash: `ae037fd6b699f6092bdf384260c4ea6cdd6676603c75af50edd17ef004585b16`

## Factorization

- invariant motor form: central canonical form plus action-conditioned PCA basis
- goal/task context: selected low-dimensional RoboMimic state/action fields
- embodiment adapter: `robosuite_panda`, start-relative canonicalization, fixed feature order
- residual side-channel: residual RMSE measured separately; `.zpbot` remains a support codec, not the schema learner

## Dataset

- family: `robomimic`
- license locator: `https://huggingface.co/datasets/robomimic/robomimic_datasets`
- actions: `can, lift, square, transport, tool_hang`
- episode count: `1000`
- feature count before canonicalization: `30`
- canonical feature count: `60`

## Scoring

Distance is reconstruction RMSE plus endpoint term plus a small covariance-aware latent-distance regularizer.
Lower score means a held-out attempt is closer to the learned action schema.
