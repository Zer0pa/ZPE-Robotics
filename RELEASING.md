<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-Robotics Masthead" width="100%">
</p>

# Releasing

<p>
  <img src=".github/assets/readme/section-bars/release-notes.svg" alt="RELEASING" width="100%">
</p>

This document defines the release decision boundary for the
`zpe-motion-kernel` workstream.

Canonical anchors:

- Repository: `https://github.com/Zer0pa/ZPE-Robotics.git`
- Package: `zpe-motion-kernel`
- Contact: `architects@zer0pa.ai`

<p>
  <img src=".github/assets/readme/section-bars/scope.svg" alt="SCOPE" width="100%">
</p>

Release statements in this repo are bounded to evidence-backed technical
claims. Package availability does not override the March 21 blocker-state.

<p>
  <img src=".github/assets/readme/section-bars/verification.svg" alt="VERIFICATION" width="100%">
</p>

| Gate | Current state | Evidence |
|---|---|---|
| package build / install surface | verified | `proofs/artifacts/operations/20260321T203557Z_technical_alignment_verification.md` |
| repo classification | standalone Python package | `proofs/runbooks/TECHNICAL_RELEASE_SURFACE.md` |
| benchmark posture | `B1`, `B2`, `B4`, and `B5` pass; `B3` fails | `proofs/enterprise_benchmark/GATE_VERDICTS.json` |
| adversarial posture | attacks `3` and `5` fail; attack `4` partially withstands | `proofs/red_team/red_team_report.json` |
| IMC runtime routing | not present | `proofs/imc_audit/imc_architecture_audit.json` |
| publish workflow | GitHub OIDC workflow aligned; PyPI UI step still open | `.github/workflows/publish.yml`, `proofs/runbooks/TRUSTED_PUBLISHING_OPERATOR_STEPS.md` |

<p>
  <img src=".github/assets/readme/section-bars/downstream-action-items.svg" alt="DOWNSTREAM ACTION ITEMS" width="100%">
</p>

Do not cut a new release narrative from the current state unless one of the
following happens first:

1. the blocker lane closes honestly, including `B3`, red-team attack `3`, and
   red-team attack `5`
2. a narrower next lane is explicitly ratified and its new acceptance gate is
   documented

If work continues on this release surface, the next concrete tasks are:

- decide whether the current no-IMC-runtime boundary stays in place or a new
  Rust-routing lane is opened
- complete the operator-only PyPI publisher registration if automatic
  publishing is desired
- publish new package metadata only after the repo docs and proof files are in
  sync with the next authorized gate
