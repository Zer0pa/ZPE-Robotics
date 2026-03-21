# RUNBOOK: E-G3 Comparator

Gate: `E-G3`
Evidence class: `infrastructure_storage_only`

## Purpose

Close the remaining sovereign blocker with one same-dataset storage comparison on the frozen arm fixture.

This runbook does not authorize policy-superiority claims. It only compares:

- comparator-side raw float32 trajectory storage
- frozen `.zpbot` packet storage on the same fixture

## Frozen Inputs

- comparator: `octo-base-1.5`
- dataset id: `arm_fixture_seed_20260220`
- fixture path: `build_fixture_bundle(seed=20260220).arm_nominal`
- packet surface: `zpbot-v2`, `wire-v1`

## Local Command

```bash
uv run python scripts/e_g3_comparator.py \
  --output proofs/reruns/e_g3_comparator_current/e_g3_comparator_result.json
```

## Hosted Command

Dispatch:

```bash
gh workflow run e_g3_comparator.yml
```

Download the artifact after the run:

```bash
gh run download <run-id> --name e_g3-comparator-evidence --dir /tmp/e_g3_comparator
```

## PASS Rule

`status=PASS` only if:

- `zpbot_storage_bytes < comparator_storage_bytes`
- the artifact preserves `authority_surface=zpbot-v2`
- the artifact preserves `compatibility_mode=wire-v1`
- `evidence_class=infrastructure_storage_only`

## What This Closes

It closes `E-G3` only as a storage and transport wedge.

It does not close:

- policy quality
- inference quality
- task success
- learned-policy superiority
