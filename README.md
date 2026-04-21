<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-Robotics Masthead" width="100%">
</p>

# ZPE-Robotics

[![Install](https://img.shields.io/badge/install-pip%20install%20--e%20.-blue)](./pyproject.toml)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue)](./pyproject.toml)
[![License](https://img.shields.io/badge/license-SAL%20v7.0-orange)](./LICENSE)

SAL v7.0 — free below $100M annual revenue. See [LICENSE](LICENSE).

---

## What This Is

<p>
  <img src=".github/assets/readme/section-bars/what-this-is.svg" alt="WHAT THIS IS" width="100%">
</p>

Searchable motion archives with VLA token export. 187× compression on real robot data. Red-team tested. `pip install zpe-robotics` (available on PyPI).

ZPE-Robotics is motion telemetry infrastructure — deterministic logging, compressed replay, and PrimitiveIndex search over joint streams. Built for robotics infrastructure teams and simulation/replay platforms where motion logs are expensive to store, slow to search, and impossible to replay deterministically. The package is public. The governing engineering surface remains blocker-state.

| Field | Value |
|-------|-------|
| Architecture | MANIFOLD_MOTION |
| Encoding | WIRE_V1 |

## Key Metrics

| Metric | Value | Baseline |
|--------|-------|----------|
| COMPRESSION | 187×† | vs zstd_l3 4.44× (42× better) |
| ENCODE_P50 | 0.11 | ms |
| VLA_TOKEN_EXPORT | 24-token FAST surface | [`vla_bridge.py`](src/zpe_robotics/vla_bridge.py) |
| BENCHMARK_GATES | 4/5 | 3 datasets, 3 families |

† Bounded-lossy. The ≤ 0.5° angular figure is limited to smooth-trajectory slices; it is not a general motion bound. Step/discontinuous inputs cause Gibbs ringing, with 68° RMSE measured on a unit-amplitude step signal. Baselines are lossless.

> Source: [`proofs/enterprise_benchmark/benchmark_result.json`](proofs/enterprise_benchmark/benchmark_result.json) | [`proofs/enterprise_benchmark/GATE_VERDICTS.json`](proofs/enterprise_benchmark/GATE_VERDICTS.json) | [`proofs/artifacts/lerobot_expanded_benchmarks/aggregate_spread_summary.json`](proofs/artifacts/lerobot_expanded_benchmarks/aggregate_spread_summary.json)

## Competitive Benchmarks

> Competitive benchmark evidence: [`proofs/enterprise_benchmark/benchmark_result.json`](proofs/enterprise_benchmark/benchmark_result.json) | [`proofs/red_team/red_team_report.json`](proofs/red_team/red_team_report.json) | [`proofs/artifacts/lerobot_expanded_benchmarks/aggregate_spread_summary.json`](proofs/artifacts/lerobot_expanded_benchmarks/aggregate_spread_summary.json)

| Tool | Compression Ratio | Notes |
|------|-------------------|-------|
| **ZPE P8** | **187.13×†** | governing LeRobot real-data benchmark; PrimitiveIndex search requires decode |
| zstd_l19 | 4.59× | strongest retained classical codec in the benchmark set |
| zstd_l3 | 4.44× | red-team attack 1 baseline; ZPE is 42.14× better |
| gzip_l9 | 3.97× | retained gzip baseline |
| mcap_zstd | 3.99× | MCAP container baseline |
| lz4_default | 3.00× | low-latency baseline |
| h5py_gzip9 | 2.69× | HDF5 gzip baseline |
| h5py_lzf | 2.15× | HDF5 fast baseline |

† Bounded-lossy. The ≤ 0.5° angular figure is limited to smooth-trajectory slices; it is not a general motion bound. Step/discontinuous inputs cause Gibbs ringing, with 68° RMSE measured on a unit-amplitude step signal. All other baselines are lossless.

## What We Prove

> Auditable guarantees backed by committed proof artifacts. Start at `docs/AUDITOR_PLAYBOOK.md`.

- Spectral wire transport with directional reasoning layer for robot action sequences
- Search operates on decoded motion streams via PrimitiveIndex
- Red-team resilience: 3 attacks withstood, 3 failed, 1 skipped — transparently reported
- VLA tokenization aligns with vision-language-action model input formats
- Public package install surface verified (available on PyPI: `pip install zpe-robotics`)

## What We Don't Claim

- Full release readiness
- Bit-exact .zpbot round-trip replay
- B3 benchmark gate pass
- Red-team resilience on attacks 3 and 5
- Robotics Rust ABI
- Generally valid ≤ 0.5° angular fidelity — the figure comes from smooth-trajectory slices only; FFT-based encoding causes Gibbs ringing on step/discontinuous inputs (68° RMSE measured on a unit-amplitude step signal)
- Search-without-decode — PrimitiveIndex requires full packet decode before indexing

## Commercial Readiness

| Field | Value |
|-------|-------|
| Verdict | BLOCKED |
| Commit SHA | c7ded78e9aea |
| Confidence | 58% |
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
| V_10 | RED-TEAM_ATTACK_5_FALSE-POSITIVE... | FAIL |
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
- The current installable package artifact is `zpe-robotics 0.1.0`, but
  the repo's March 21 blocker-state docs remain the authority surface for
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

### Expanded LeRobot Benchmark Coverage

The expanded benchmark sweep is recorded in
`proofs/artifacts/lerobot_expanded_benchmarks/`. The current qualified surface
covers `3` real datasets across `3` materially distinct families, with
compression ratios spanning `58.70x` to `186.05x`.

| Dataset | Family | Compression ratio | Status |
|---|---|---:|---|
| `lerobot/columbia_cairlab_pusht_real` | `pusht` | `186.05x` | qualified |
| `lerobot/aloha_mobile_shrimp` | `aloha` | `61.27x` | qualified |
| `lerobot/umi_cup_in_the_wild` | `umi` | `58.70x` | qualified |
| `lerobot/pusht_image` | `pusht` | n/a | skipped: insufficient joint dimension |

Read `proofs/artifacts/lerobot_expanded_benchmarks/aggregate_spread_summary.json`
for the rollup verdict and
`proofs/artifacts/lerobot_expanded_benchmarks/dataset_manifest.json` for the
full attempt ledger, including qualification misses that were preserved rather
than averaged away.

## Repo Shape

<p>
  <img src=".github/assets/readme/section-bars/repo-shape.svg" alt="REPO SHAPE" width="100%">
</p>

| Field | Value |
|-------|-------|
| Proof Anchors | 6 |
| Modality Lanes | 3 |
| Authority Source | `proofs/ENGINEERING_BLOCKERS.md` |

The modality-lane count reflects the three recorded parity lanes
(`arm64-qemu`, `macos`, `ubuntu-x86`) in
`proofs/release_candidate/it04_parity_matrix_result.json`.

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
| Repository | `https://github.com/Zer0pa/ZPE-Robotics.git` |
| Package / import / CLI | `zpe-robotics` / `zpe_robotics` / `zpe-robotics` |
| Acquisition surface | `pip install zpe-robotics` (available on PyPI) |
| License | `LicenseRef-Zer0pa-SAL-6.2` |
| Contact | `architects@zer0pa.ai` |
| Release state | public repo and published package; engineering surface remains blocker-governed |
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

Install from PyPI:

```bash
pip install zpe-robotics
zpe-robotics --version
```

Or install from source (development):

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
If you need the release workflow boundary, use `RELEASING.md`.

<p>
  <img src=".github/assets/readme/section-bars/contributing-security-support.svg" alt="CONTRIBUTING, SECURITY, SUPPORT" width="100%">
</p>

| Need | Route |
|---|---|
| Contributor workflow | `CONTRIBUTING.md` |
| Security reporting | `SECURITY.md` |
| Governance and claim policy | `GOVERNANCE.md` |
| Support routing | `docs/SUPPORT.md` |
| Docs index | `docs/README.md` |
| Operator commands | `docs/OPERATOR_RUNBOOK.md` |

## Ecosystem

ZPE-Robotics follows the portfolio release-hygiene pattern used by
[ZPE-IMC](https://github.com/Zer0pa/ZPE-IMC), but it does not inherit IMC
runtime claims, benchmark verdicts, or release readiness by association.

| Need | Route |
|---|---|
| Robotics-to-IMC boundary | `docs/family/ROBOTICS_RELEASE_LINKAGE.md` |
| Frozen proof lineage note | `proofs/README_LINEAGE_PATHS.md` |
| Reference core repo | `https://github.com/Zer0pa/ZPE-IMC` |

**Observability:** [Comet dashboard](https://www.comet.com/zer0pa/zpe-robotics/view/new/panels) (public)

## Who This Is For

| | |
|---|---|
| **Ideal first buyer** | Robotics infrastructure team or simulation/replay platform |
| **Pain** | Robot telemetry archives grow fast and can only be searched after full decompression — replay pipelines lack determinism guarantees |
| **Deployment** | Public Python package — `pip install zpe-robotics` |
| **Family position** | Product candidate in the Zer0pa deterministic encoding family. ZPE-IMC is the umbrella integration layer |
