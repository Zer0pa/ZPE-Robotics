<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-Robotics Masthead" width="100%">
</p>

# ZPE-Robotics

[![Install](https://img.shields.io/badge/install-pip%20install%20--e%20.-blue)](./pyproject.toml)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue)](./pyproject.toml)
[![SAL v7.0](https://img.shields.io/badge/license-SAL%20v7.0-orange)](./LICENSE)

SAL v7.0 — free below $100M annual revenue. See [LICENSE](LICENSE).

---

## What This Is

<p>
  <img src=".github/assets/readme/section-bars/what-this-is.svg" alt="WHAT THIS IS" width="100%">
</p>

Deterministic motion logging, compressed replay, PrimitiveIndex search, and FAST VLA token export on the current blocker-governed authority surface.

ZPE-Robotics is motion telemetry infrastructure for robotics infrastructure teams and simulation/replay platforms where motion logs are expensive to store, slow to search, and difficult to replay deterministically. The governing engineering surface remains blocker-state.

## Verified Runtime Surfaces

| Surface | Evidence |
|--------|----------|
| Packet encode / verify / decode CLI | [`tests/test_cli.py`](tests/test_cli.py) |
| PrimitiveIndex decoded-stream search | [`tests/test_primitive_index.py`](tests/test_primitive_index.py) |
| FAST VLA token export | [`tests/test_vla_bridge.py`](tests/test_vla_bridge.py) |
| Anomaly threshold gate | [`tests/test_anomaly.py`](tests/test_anomaly.py) |
| Canonical reference packet parity | [`tests/test_release_candidate.py`](tests/test_release_candidate.py) |

## What We Prove

> Auditable guarantees backed by committed proof artifacts. Start at `docs/AUDITOR_PLAYBOOK.md`.

- Wire-v1 packet encode, decode, and verification surfaces are exercised in the committed CLI and test suite
- Search operates on decoded motion streams via PrimitiveIndex
- VLA token export emits the committed FAST token surface
- The current anomaly threshold surface selects `3.22` while meeting the false-positive and recall gates
- Canonical reference packet parity is frozen to the committed bridge hash

## What We Don't Claim

- Full release readiness
- Bit-exact .zpbot round-trip replay
- B3 benchmark gate pass
- Red-team closure on attack `3` or independent third-party reproduction
- Robotics Rust ABI
- Generally valid ≤ 0.5° angular fidelity — the figure comes from smooth-trajectory slices only; FFT-based encoding causes Gibbs ringing on step/discontinuous inputs (68° RMSE measured on a unit-amplitude step signal)
- Search-without-decode — PrimitiveIndex requires full packet decode before indexing

## Commercial Readiness

| Field | Value |
|-------|-------|
| Verdict | BLOCKED |
| Source | proofs/FINAL_STATUS.md |

## Tests and Verification

| Code | Check | Verdict |
|------|-------|---------|
| V_01 | BENCHMARK_GATE_B1_COMPRESSION | PASS |
| V_02 | BENCHMARK_GATE_B2_ZSTD_BASELINE | PASS |
| V_03 | BENCHMARK_GATE_B3_BIT-EXACT_+_SE... | FAIL |
| V_04 | BENCHMARK_GATE_B4_ENCODE_LATENCY | PASS |
| V_05 | BENCHMARK_GATE_B5_DECODE_LATENCY | PASS |
| V_06 | RED-TEAM_ATTACK_1_BASELINE | PASS |
| V_07 | RED-TEAM_ATTACK_2_ENTROPY | PASS |
| V_08 | RED-TEAM_ATTACK_3_LOSSLESS_QUALI... | FAIL |
| V_09 | RED-TEAM_ATTACK_4_CORPUS_ADEQUACY | INC |
| V_10 | RED-TEAM_ATTACK_5_FALSE-POSITIVE... | PASS |
| V_11 | RED-TEAM_ATTACK_6_PYTHON_3.12_PA... | PASS |
| V_12 | RED-TEAM_ATTACK_7_EXTERNAL_REPRO... | INC |

<p>
  <img src=".github/assets/readme/zpe-masthead-option-3-2.gif" alt="ZPE-Robotics Masthead Detail 3.2" width="100%">
</p>

## Proof Anchors

<p>
  <img src=".github/assets/readme/section-bars/evidence-and-claims.svg" alt="EVIDENCE AND CLAIMS" width="100%">
</p>

| Path | State |
|------|-------|
| `proofs/ENGINEERING_BLOCKERS.md` | VERIFIED |
| `proofs/enterprise_benchmark/GATE_VERDICTS.json` | VERIFIED |
| `proofs/red_team/red_team_report.json` | VERIFIED |
| `proofs/release_candidate/clean_clone_result.json` | VERIFIED |
| `proofs/release_candidate/it04_parity_matrix_result.json` | VERIFIED |
| `proofs/imc_audit/imc_architecture_audit.json` | VERIFIED |

- Runtime and proof artifacts outrank prose.
- `GO` and `NO-GO` language is reserved for named gates only.
- Historical proof bundles remain lineage only. They do not override the March
  21 blocker-state evidence.
- No IMC runtime import is introduced by this repo.
- The repo's March 21 blocker-state docs remain the authority surface for
  engineering status.

Use these files together:

| Need | Read first |
|---|---|
| Current blocker truth | `proofs/ENGINEERING_BLOCKERS.md` |
| Benchmark verdicts | `proofs/enterprise_benchmark/GATE_VERDICTS.json` |
| Adversarial findings | `proofs/red_team/red_team_report.json` |
| Package/runtime boundary | `proofs/runbooks/TECHNICAL_RELEASE_SURFACE.md` |
| Release-candidate note | `docs/RELEASE_CANDIDATE.md` |
| Citation record | `CITATION.cff` |
| Docs registry | `docs/DOC_REGISTRY.md` |
| Historical lineage | `proofs/artifacts/historical/README.md` |

## Repo Shape

<p>
  <img src=".github/assets/readme/section-bars/repo-shape.svg" alt="REPO SHAPE" width="100%">
</p>

| Area | Purpose |
|---|---|
| `src/zpe_robotics/` | package implementation, CLI, packet handling, search, anomaly, and audit logic |
| `tests/` | release-surface, CLI, codec, and regression checks |
| `scripts/` | replay, benchmark, falsification, and clean-clone helpers |
| `docs/` | front-door, architecture, support, legal, and family-linkage docs |
| `proofs/` | blockers, benchmark artifacts, red-team outputs, release runbooks, and historical bundles |
| `.github/workflows/` | CI, clean-clone, parity, comparator, and publish workflows |

<p>
  <img src=".github/assets/readme/zpe-masthead-option-3-3.gif" alt="ZPE-Robotics Masthead Detail 3.3" width="100%">
</p>

## Quick Start

<p>
  <img src=".github/assets/readme/section-bars/quickstart-and-authority-point.svg" alt="QUICKSTART AND AUTHORITY POINT" width="100%">
</p>

| Surface | Current truth |
|---|---|
| Package / import / CLI | `zpe-robotics` / `zpe_robotics` / `zpe-robotics` |
| Acquisition surface | source install from this repository |
| License | `LicenseRef-Zer0pa-SAL-7.0` |
| Release state | engineering surface remains blocker-governed |
| Engineering | not complete |
| Current authority | `proofs/ENGINEERING_BLOCKERS.md` |

| Authority layer | File |
|---|---|
| governing blocker state | `proofs/ENGINEERING_BLOCKERS.md` |
| benchmark gate verdicts | `proofs/enterprise_benchmark/GATE_VERDICTS.json` |
| adversarial verdicts | `proofs/red_team/red_team_report.json` |
| package/runtime boundary | `proofs/runbooks/TECHNICAL_RELEASE_SURFACE.md` |
| IMC integration boundary | `proofs/imc_audit/imc_architecture_audit.json` |

<p>
  <img src=".github/assets/readme/section-bars/setup-and-verification.svg" alt="SETUP AND VERIFICATION" width="100%">
</p>

Install from source:

```bash
pip install -e .
zpe-robotics --version
```

Repo-local engineering surface:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[dev,benchmark,telemetry,netnew]"
python -m pytest tests -q
python -m build
```

If you need the shortest honest verification route, use
`docs/AUDITOR_PLAYBOOK.md`.
If you need the release workflow boundary, use
`proofs/runbooks/TECHNICAL_RELEASE_SURFACE.md`.

<p>
  <img src=".github/assets/readme/section-bars/contributing-security-support.svg" alt="CONTRIBUTING, SECURITY, SUPPORT" width="100%">
</p>

| Need | Route |
|---|---|
| Security reporting | `SECURITY.md` |
| Claim boundary | `docs/LEGAL_BOUNDARIES.md` |
| Support routing | `docs/SUPPORT.md` |
| Docs index | `docs/README.md` |
| Operator commands | `docs/OPERATOR_RUNBOOK.md` |
