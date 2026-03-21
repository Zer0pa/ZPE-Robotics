# Gate E-G1..E-G5 Runbook: NET-NEW Ingestion and RunPod Readiness

## Objective
Satisfy Appendix E attempt-all, impracticality discipline, and RunPod deferment packaging.

## Commands
1. `RUN_ROOT="proofs/reruns/robotics_wave1_$(date -u +%Y%m%dT%H%M%SZ)"`
2. `python scripts/run_wave1.py --output-root "$RUN_ROOT" --seed 20260220 --determinism-runs 5 --max-wave`
3. `python scripts/validate_net_new.py --artifacts "$RUN_ROOT"`
4. `python scripts/net_new_ingest.py --output-root "$RUN_ROOT" --seed 20260220 --sample-size 128`

## Required Artifacts
1. `max_resource_lock.json`
2. `max_resource_validation_log.md`
3. `max_claim_resource_map.json`
4. `impracticality_decisions.json`
5. `cross_embodiment_consistency_report.json`
6. `policy_impact_delta_report.json`
7. `net_new_gap_closure_matrix.json`
8. `runpod_readiness_manifest.json` (mandatory when `IMP-COMPUTE` exists)
9. `runpod_exec_plan.md` (mandatory when `IMP-COMPUTE` exists)
10. `runpod_requirements_lock.txt` (mandatory when `IMP-COMPUTE` exists)
11. `runpod_expected_artifacts_manifest.json` (mandatory when `IMP-COMPUTE` exists)

## Fail Signatures
- Missing E3 attempt evidence
- Invalid IMP code outside allowed set
- Claim closure lacking resource linkage
- Missing RunPod artifacts when compute was deferred
- RunPod package missing pinned deps or exact command chain
- Any unresolved gap left as `INCONCLUSIVE` at final closure

## Final Closure Rules
1. Non-negotiable runtime gaps unresolved after declared attempts must be explicit `FAIL` with evidence.
2. If commercialization/license restrictions block required runtime and no commercial-safe open alternative exists, use `PAUSED_EXTERNAL` with evidence.

## Rollback
- Patch metadata/evidence emission only.
- Re-execute E-gates and packaging gate.
