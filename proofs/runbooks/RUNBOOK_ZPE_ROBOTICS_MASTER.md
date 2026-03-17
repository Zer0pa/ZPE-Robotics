# RUNBOOK: ZPE Robotics Wave-1 Master

- Scope root: repo root
- Historical PRD: preserved outside the repo in the outer workspace shell
- Historical startup prompt: preserved outside the repo in the outer workspace shell
- Concept anchor: not bundled in this repo; historical planning references remain outside the repo
- Rubric: not bundled in this repo; use current repo truth and proof surfaces instead

## 1) Strict Gate Order (No Skip)
1. Gate A: Runbook + fixture/resource lock
2. Gate B: Core codec + fidelity/compression baselines
3. Gate C: rosbag/primitive integration checks
4. Gate D: malformed/adversarial/determinism campaigns
5. Gate E: artifact packaging + claim adjudication
6. Gate M1: rosbag roundtrip + live callback/runtime path checks
7. Gate M2: LeRobot/LIBERO direct-run checks (non-proxy attempts mandatory)
8. Gate M3: MuJoCo fidelity parity run (or documented IMP with evidence)
9. Gate M4: VLA token quality on real-task corpora (or documented IMP with evidence)
10. Gate E-G1: 100% attempt coverage for E3 resources with command evidence
11. Gate E-G2: Multi-embodiment evidence check (single-robot-only closure prohibited)
12. Gate E-G3: Octo policy-impact comparator evidence
13. Gate E-G4: Every skip must have valid `IMP-*` code + signature + impact
14. Gate E-G5: RunPod readiness artifacts complete for compute deferments

## 2) Deterministic Seed Policy
- Global seed: `20260220`
- RNG engine: `numpy.random.default_rng`
- Sub-seeds:
  - arm corpus: `20260221`
  - humanoid corpus: `20260222`
  - primitive library/query generation: `20260223`
  - anomaly injections: `20260224`
  - determinism replay perturbation-free checks: `20260225`
- Prohibition: no implicit RNG via global `np.random` state.

## 3) Command Ledger (Predeclared)
| ID | Command | Expected output | Fail signatures | Rollback |
|---|---|---|---|---|
| CL-01 | `python -m pytest -q` | all tests pass | non-zero exit, assertion failure, uncaught exception | patch failing module, rerun CL-01 + downstream |
| CL-02 | `python scripts/run_wave1.py --output-root proofs/reruns/robotics_wave1_local --seed 20260220 --determinism-runs 5` | all gates PASS, artifacts emitted | missing artifact, threshold breach, crash | revert to last green module snapshot, rerun from failed gate |
| CL-03 | `python scripts/run_wave1.py --output-root proofs/reruns/robotics_wave1_local_replay --seed 20260220 --determinism-runs 5` | same determinism hashes as CL-02 | hash drift, metric drift | inspect nondeterministic path, enforce seeded order, rerun CL-02 onward |
| CL-04 | `python scripts/regression_pack.py --artifacts proofs/reruns/robotics_wave1_local` | regression PASS, zero uncaught crashes | timeout, crash, mismatch | patch isolated regression defect, rerun CL-04 + Gate E |
| CL-05 | `python scripts/run_wave1.py --output-root proofs/reruns/robotics_wave1_local --seed 20260220 --determinism-runs 5 --max-wave` | A-E + M/E gates evaluated and max-wave artifacts emitted | missing max artifacts, unattempted resources, invalid IMP code | patch resource-ingestion path, rerun from failed M/E gate |
| CL-06 | `python scripts/validate_net_new.py --artifacts proofs/reruns/robotics_wave1_local` | net-new artifact integrity PASS | missing evidence links, malformed impracticality records | patch validation fields + rerun CL-06 |
| CL-07 | `PATH=/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin /opt/homebrew/bin/colima start --cpu 4 --memory 8 --disk 60` | arm64 Colima runtime ready and Docker daemon reachable | `limactl is running under rosetta`, `Cannot connect to the Docker daemon` | enforce arm64 PATH/bin, rerun CL-07 + failed gate |

## 4) Falsification-First Claim Matrix
| Claim | Null hypothesis (to falsify) | Attack/test command | Promotion evidence |
|---|---|---|---|
| ROB-C001 | arm CR < 15x | CL-02 + DT-ROB-2 | `robot_arm_benchmark.json` |
| ROB-C002 | humanoid CR < 12x | CL-02 + DT-ROB-2 | `robot_humanoid_benchmark.json` |
| ROB-C003 | EE RMSE > 0.1 mm | CL-02 + DT-ROB-1/2 | `robot_ee_fidelity.json` |
| ROB-C004 | joint RMSE > 0.05 deg | CL-02 + DT-ROB-1/2 | `robot_joint_fidelity.json` |
| ROB-C005 | P@10 < 0.90 | CL-02 + DT-ROB-5 | `robot_primitive_search_eval.json` |
| ROB-C006 | rosbag roundtrip not bit-consistent | CL-02 + DT-ROB-3 | `robot_rosbag_roundtrip.json` |
| ROB-C007 | anomaly recall < 0.90 | CL-02 + DT-ROB-2 | `robot_anomaly_eval.json` |
| ROB-C008 | VLA token quality <= naive baseline | CL-02 + DT-ROB-5 | `robot_vla_token_eval.json` |

## 5) Expected Artifact Root
- `proofs/reruns/robotics_wave1_local/`

## 6) Failure Signatures (Global)
1. Determinism drift: mismatched SHA-256 across replay runs.
2. Crash signature: uncaught exception stack trace in malformed/adversarial suites.
3. Fidelity breach: `ee_rmse_mm > 0.1` or `joint_rmse_deg > 0.05`.
4. Compression breach: `compression_ratio` below claim threshold.
5. Primitive quality breach: `precision_at_10 < 0.90`.

## 7) Rollback Policy
1. Keep gate checkpoints as immutable JSON snapshots under artifact root.
2. On gate failure, patch minimal defect only in affected module.
3. Rerun failed gate + all downstream gates in strict order.
4. Do not relax thresholds for pass.

## 8) Resource Lock + Fallback Plan
| Resource/checklist item | Preferred resource | Fallback if blocked | Comparability impact policy |
|---|---|---|---|
| LeRobot integration path | local adapter contract + schema fixture | synthetic LeRobot-like schema fixture | mark integration readiness as partial if no native runtime |
| LIBERO-100 benchmark | local LIBERO trajectory fixture (task-structured synthetic proxy) | deterministic synthetic manipulation corpus | keep cross-paper comparability INCONCLUSIVE |
| rosbag2 MCAP path | in-lane MCAP-compatible adapter shim | deterministic binary bag shim | claim remains PASS only for tested shim scope |
| MoveIt2 interoperability | message contract fixture for planned/executed trajectory logs | simulated MoveIt2 callback payloads | mark runtime integration INCONCLUSIVE |
| Isaac GR00T N1.5 | schema compatibility check against documented fields | synthetic GR00T-style trajectory sample | mark runtime on Isaac as INCONCLUSIVE |
| FAST + CubicVLA comparators | FAST-like DCT token baseline + Cubic-style spline proxy | naive binning + DCT proxy | note comparator fidelity limitations explicitly |
| robot_descriptions URDF path | URDF fixture parser compatibility tests | minimal URDF parser with generated model | mark external package dependency unmet as INCONCLUSIVE |
| MuJoCo simulation validation | MuJoCo-compatible kinematic replay adapter | analytic FK replay simulator | mark physics-engine parity INCONCLUSIVE |

## 9) Dataset/Resource Provenance Lock
- Synthetic corpora generator: `src/zpe_robotics/fixtures.py` (seed-bound; hash captured in manifest)
- Baseline comparators: in-lane deterministic implementations (naive binning, DCT proxy)
- Snapshot metadata fields captured in `concept_resource_traceability.json`:
  - `resource_name`
  - `source_reference`
  - `access_date`
  - `version_or_snapshot`
  - `evidence_artifact`

## 10) Concept Open Questions Resolution Plan
Open questions from concept doc Section 11 are resolved with statuses:
- `RESOLVED`: direct in-lane executable evidence.
- `INCONCLUSIVE`: substitution used; equivalence not proven.
- `OUT-OF-SCOPE`: outside Wave-1 runtime boundary, documented with rationale.

## 11) Maximalization + NET-NEW Resource Lock
Mandatory external resources to attempt (E3):
1. AgiBot World
2. Open X-Embodiment
3. RH20T
4. Octo policy comparator

Required artifacts:
1. `max_resource_lock.json`
2. `max_resource_validation_log.md`
3. `max_claim_resource_map.json`
4. `impracticality_decisions.json`
5. `cross_embodiment_consistency_report.json`
6. `policy_impact_delta_report.json`
7. `net_new_gap_closure_matrix.json`
8. `runpod_readiness_manifest.json` (mandatory for `IMP-COMPUTE`)
9. `runpod_exec_plan.md` (mandatory dry-run handoff for deferred GPU paths)

Allowed impracticality codes only:
- `IMP-LICENSE`
- `IMP-ACCESS`
- `IMP-COMPUTE`
- `IMP-STORAGE`
- `IMP-NOCODE`

Each impracticality record must include:
1. command evidence
2. error signature
3. fallback path
4. claim-impact note

## 12) Final-Phase Closure Adjudication (2026-02-21)
Status vocabulary for unresolved runtime gates:
1. `PASS`: full native/runtime evidence present in artifacts.
2. `FAIL`: falsification succeeded or required runtime path unavailable after declared attempts.
3. `PAUSED_EXTERNAL`: required path blocked by commercialization/license restrictions and no commercial-safe open alternative is available.

Promotion constraints:
1. No claim or gap may stay `INCONCLUSIVE` at final closure.
2. Any `FAIL`/`PAUSED_EXTERNAL` must include concrete artifact evidence paths.
3. `PAUSED_EXTERNAL` requires license/access evidence plus explicit open-alternative search evidence.

## 13) Closure Command Chain (Mac -> GPU-ready)
1. `set -a; [ -f .env ] && source .env; set +a`
2. `python scripts/run_wave1.py --output-root proofs/reruns/robotics_wave1_local --seed 20260220 --determinism-runs 5 --max-wave --dry-lock-only`
3. `python scripts/run_wave1.py --output-root proofs/reruns/robotics_wave1_local --seed 20260220 --determinism-runs 5 --max-wave`
4. `python scripts/validate_net_new.py --artifacts proofs/reruns/robotics_wave1_local`
5. `python scripts/regression_pack.py --artifacts proofs/reruns/robotics_wave1_local`
6. `python -m pytest -q`

Additional runtime-closure probes:
1. ROS2 path: `ros2 pkg list`, record version provenance separately, then container/runtime alternatives (if available), else explicit `FAIL`.
2. MuJoCo path: arm64 Python 3.11 runtime probe with deterministic parity script before claim update.
3. Octo GPU-dependent path: local dry-run + RunPod handoff artifacts with pinned dependencies and exact command chain.
4. ROS2 docker daemon recovery: `PATH=/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin /opt/homebrew/bin/colima start --cpu 4 --memory 8 --disk 60`.
