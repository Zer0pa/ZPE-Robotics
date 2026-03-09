# Gate A Runbook: Resource Lock and Planning

## Objective
Finalize execution contract before coding.

## Steps
1. Confirm latest startup prompt and PRD were read.
2. Lock deterministic seed policy.
3. Predeclare command ledger, fail signatures, rollback.
4. Predeclare falsification strategy for ROB-C001..ROB-C008.
5. Predeclare concept traceability coverage for Appendix B items.
6. Predeclare Appendix D maximalization gates (M1-M4).
7. Predeclare Appendix E NET-NEW ingestion gates (E-G1..E-G5).
8. Execute environment bootstrap and tokenized-access verification from `.env`.

## Commands
1. `ls -la`
2. `sed -n '1,260p' STARTUP_PROMPT_ZPE_ROBOTICS_SECTOR_AGENT_2026-02-20.md`
3. `sed -n '1,260p' PRD_ZPE_ROBOTICS_SECTOR_EXPANSION_WAVE1_2026-02-20.md`
4. `set -a; [ -f .env ] && source .env; set +a`
5. `python scripts/run_wave1.py --output-root proofs/reruns/robotics_wave1_local --seed 20260220 --determinism-runs 5 --max-wave --dry-lock-only`

## Expected Outputs
- `runbooks/RUNBOOK_ZPE_ROBOTICS_MASTER.md`
- `runbooks/RUNBOOK_GATE_A_RESOURCE_LOCK.md`
- Gate runbooks B-E drafted
- Max-wave and NET-NEW runbook coverage drafted
- `max_resource_lock.json` seed/resource lock initialized

## Fail Signatures
- Missing mandatory runbook sections.
- Unseeded random policy.
- Undefined rollback path.
- `.env` sourcing failure or missing tokenized access keys.
- Missing E3 attempt plan or invalid IMP-code policy.

## Rollback
- Rewrite runbook sections before any source code creation.
