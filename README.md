<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-Robotics Masthead" width="100%">
</p>

# ZPE-Robotics

**187× compression on real robot data.**

[![PyPI](https://img.shields.io/pypi/v/zpe-robotics)](https://pypi.org/project/zpe-robotics/)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue)](./pyproject.toml)
[![License](https://img.shields.io/badge/license-SAL%20v6.0-orange)](./LICENSE)

SAL v6.0. Free below $100M annual revenue. See [LICENSE](LICENSE).

---

## What This Is

Motion telemetry infrastructure. Deterministic logging. Compressed replay. Search without decode.

**187× compression** on `lerobot/columbia_cairlab_pusht_real`. Frozen `wire-v1` transport. Search without decode. Red-team attacks 1, 2, 6 withstood. Install: `pip install zpe-robotics`.

Active B3 engineering. Active red-team closure work. `.zpbot` replay proof still open.

| Anchor | Artifact |
|---|---|
| Benchmark gate verdicts | [`GATE_VERDICTS.json`](proofs/enterprise_benchmark/GATE_VERDICTS.json) |
| Red-team report | [`red_team_report.json`](proofs/red_team/red_team_report.json) |
| Engineering blockers | [`ENGINEERING_BLOCKERS.md`](proofs/ENGINEERING_BLOCKERS.md) |

---

**Not claimed:** full release readiness, bit-exact `.zpbot` round-trip replay, B3 gate pass, red-team resilience on attacks 3/5, or Rust ABI.

<p>
  <img src=".github/assets/readme/section-bars/what-this-is.svg" alt="WHAT THIS IS" width="100%">
</p>

ZPE-Robotics is the public repository for the `zpe-robotics` package.
The current public artifact is a standalone Python package for frozen
`wire-v1` motion transport, replay, search, and audit workflows. The repo and
package are public, but the governing engineering surface remains blocker-state
and is not a full robotics-platform release.

<p>
  <img src=".github/assets/readme/section-bars/quickstart-and-authority-point.svg" alt="QUICKSTART AND AUTHORITY POINT" width="100%">
</p>

| Surface | Current truth |
|---|---|
| Repository | `https://github.com/Zer0pa/ZPE-Robotics.git` |
| Package / import / CLI | `zpe-robotics` / `zpe_robotics` / `zpe-robotics` |
| Acquisition surface | `pip install zpe-robotics` |
| License | `LicenseRef-Zer0pa-SAL-6.0` |
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
  <img src=".github/assets/readme/section-bars/lane-status-snapshot.svg" alt="LANE STATUS SNAPSHOT" width="100%">
</p>

| Surface | Current truth |
|---|---|
| Benchmark gates | `B1`, `B2`, `B4`, and `B5` pass; `B3` fails |
| Real-data benchmark | `187.1345x` on `lerobot/columbia_cairlab_pusht_real` |
| Red-team | attacks `1`, `2`, and `6` withstand; `4` partially withstands; `3` and `5` fail; `7` remains open |
| Replay claim boundary | strict bit-exact replay is not proven on the current `.zpbot` round-trip |
| Searchability | supported without decode on the benchmark surface |
| Rust integration | no robotics `.zpbot` Rust ABI is wired into this repo |
| Release workflow | GitHub OIDC workflow is aligned; PyPI UI registration is still operator-only |
| Release-ready verdict | not authorized; public visibility does not erase blockers |

<p>
  <img src=".github/assets/readme/zpe-masthead-option-3-2.gif" alt="ZPE-Robotics Masthead Detail 3.2" width="100%">
</p>

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
  <img src=".github/assets/readme/section-bars/evidence-and-claims.svg" alt="EVIDENCE AND CLAIMS" width="100%">
</p>

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

<p>
  <img src=".github/assets/readme/zpe-masthead-option-3-3.gif" alt="ZPE-Robotics Masthead Detail 3.3" width="100%">
</p>

<p>
  <img src=".github/assets/readme/section-bars/setup-and-verification.svg" alt="SETUP AND VERIFICATION" width="100%">
</p>

Public package install:

```bash
pip install zpe-robotics
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

## Expanded LeRobot Benchmark Coverage

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

## Ecosystem Cross-Links

ZPE-Robotics follows the portfolio release-hygiene pattern used by
[ZPE-IMC](https://github.com/Zer0pa/ZPE-IMC), but it does not inherit IMC
runtime claims, benchmark verdicts, or release readiness by association.

| Need | Route |
|---|---|
| Robotics-to-IMC boundary | `docs/family/ROBOTICS_RELEASE_LINKAGE.md` |
| Frozen proof lineage note | `proofs/README_LINEAGE_PATHS.md` |
| Reference core repo | `https://github.com/Zer0pa/ZPE-IMC` |
