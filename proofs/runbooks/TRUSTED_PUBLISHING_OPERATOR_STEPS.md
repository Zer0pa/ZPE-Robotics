# Trusted Publishing Operator Steps

## Scope

This runbook records the operator-only PyPI setup boundary. It does not change
the current workflow and does not enable any external system state.

## Current State

- The current package is `zpe-robotics`.
- The current publish workflow is `.github/workflows/publish.yml`.
- Wave 2 is responsible for migrating this lane to reusable workflow callers and
  Trusted Publishing with PEP 740 attestations.

## Operator Steps For Wave 2

1. Confirm the PyPI project is owned by the expected Zer0pa operator account.
2. Configure PyPI Trusted Publishing for `Zer0pa/ZPE-Robotics`.
3. Bind the release workflow environment expected by the Wave 2 reusable caller.
4. Remove token-based publishing only in the Wave 2 workflow migration PR.
5. Cut a tag only after owner review confirms the lane migration PR is merged.

## Non-Goals

- No PyPI publish is authorized by this runbook.
- No GitHub workflow edit is included in the lane hygiene pass.
- No Zenodo or Hugging Face external state is changed here.
