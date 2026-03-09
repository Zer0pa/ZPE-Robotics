# Architecture

## Repo Layout

| Path | Purpose |
|---|---|
| `src/zpe_robotics/` | package implementation |
| `tests/` | repo test surface |
| `scripts/` | execution, validation, and regression entrypoints |
| `docs/` | front-door, status, legal, and linkage docs |
| `proofs/` | proof indexes, logs, historical artifacts, and runbooks |

## Package Modules

| Module | Responsibility |
|---|---|
| `codec.py` | trajectory codec and compression metrics |
| `rosbag_adapter.py` | bag serialization, corruption, and roundtrip evaluation |
| `fixtures.py` | deterministic fixture generation |
| `kinematics.py` | RMSE and end-effector fidelity helpers |
| `primitives.py` | primitive corpus generation and retrieval metrics |
| `anomaly.py` | anomaly injection and detection metrics |
| `vla_eval.py` | token quality evaluation |
| `falsification.py` | adversarial and malformed-data campaigns |
| `determinism.py` | replay hashing |
| `constants.py` | claim thresholds and artifact contracts |

## Proof Model

There are three proof classes in this repo:

1. Current status docs:
   - `proofs/FINAL_STATUS.md`
   - `proofs/CONSOLIDATED_PROOF_REPORT.md`
2. Current pre-repo authority summary:
   - `proofs/logs/PRE_REPO_AUTHORITY_SNAPSHOT_2026-03-09.md`
3. Historical bundles:
   - `proofs/artifacts/historical/2026-02-20_zpe_robotics_wave1/`
   - `proofs/artifacts/historical/2026-02-21_zpe_robotics_wave1_closure/`

Historical bundles are preserved exactly enough for lineage, including old path
residue. They are not the current portability standard.

## Execution Path

- lightweight checks: `pytest tests -q`
- full rerun path when Phase 5 opens:
  - `scripts/run_wave1.py`
  - `scripts/validate_net_new.py`
  - `scripts/regression_pack.py`

Default rerun output root is now `proofs/reruns/robotics_wave1_local`.
