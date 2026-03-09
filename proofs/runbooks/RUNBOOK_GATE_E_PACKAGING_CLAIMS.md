# Gate E Runbook: Packaging and Claim Adjudication

## Objective
Finalize artifact contract, quality scorecard, innovation delta, and GO/NO-GO decision.

## Commands
1. `python scripts/run_wave1.py --output-root proofs/reruns/robotics_wave1_local --seed 20260220 --determinism-runs 5`
2. `python scripts/regression_pack.py --artifacts proofs/reruns/robotics_wave1_local`
3. `python scripts/validate_net_new.py --artifacts proofs/reruns/robotics_wave1_local`

## Required Outputs
- Core PRD artifacts (15 files)
- Appendix C artifacts:
  - `quality_gate_scorecard.json`
  - `innovation_delta_report.md`
  - `integration_readiness_contract.json`
  - `residual_risk_register.md`
  - `concept_open_questions_resolution.md`
  - `concept_resource_traceability.json`
- Appendix E/NET-NEW artifacts:
  - `max_resource_lock.json`
  - `max_resource_validation_log.md`
  - `max_claim_resource_map.json`
  - `impracticality_decisions.json`
  - `cross_embodiment_consistency_report.json`
  - `policy_impact_delta_report.json`
  - `net_new_gap_closure_matrix.json`
  - `runpod_readiness_manifest.json` (if any `IMP-COMPUTE`)
  - `runpod_exec_plan.md` (if any `IMP-COMPUTE`)

## Claim Promotion Rule
- Upgrade claims only if evidence path exists and metric threshold is met.
- Keep uncertain results `INCONCLUSIVE`.

## Rollback
- If artifact contract incomplete, regenerate manifest and adjudication outputs only.
