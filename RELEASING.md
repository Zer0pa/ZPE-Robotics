# Releasing

## Current Boundary

`zpe-robotics 0.1.0` is published on PyPI. The engineering authority remains
blocker-governed by `proofs/ENGINEERING_BLOCKERS.md`; public package
availability is not a full release-readiness verdict.

## Release Gates

Before a release can be treated as authority-bearing:

1. `python -m pytest tests -q` passes on the supported runtime matrix.
2. Benchmark gates are reconciled in `proofs/enterprise_benchmark/GATE_VERDICTS.json`.
3. Red-team findings are reconciled in `proofs/red_team/red_team_report.json`.
4. IMC/runtime boundary remains explicit in `proofs/imc_audit/imc_architecture_audit.json`.
5. Proof anchors cited by `README.md` resolve in the repo.

## Operator Boundary

Do not publish from lane-hygiene branches. Workflow migration, Trusted
Publishing, PEP 740 attestations, and reusable workflow callers are Wave 2 work.

The current workflow file is `.github/workflows/publish.yml`; this document does
not modify or authorize that workflow.
