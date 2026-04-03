<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-Robotics Masthead" width="100%">
</p>

# ZPE-Robotics

[![PyPI](https://img.shields.io/pypi/v/zpe-motion-kernel)](https://pypi.org/project/zpe-motion-kernel/)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue)](./pyproject.toml)
[![License](https://img.shields.io/badge/license-SAL%20v6.0-orange)](./LICENSE)

---

## What This Is

ZPE-Robotics is a deterministic motion transport and replay kernel for robotics telemetry, search, and audit workflows, available as `pip install zpe-motion-kernel`.

## Commercial Wedge

This is for **robotics infrastructure teams, simulation/replay teams, and OEM robotics telemetry teams** who need deterministic motion logging with searchable archives and auditable replay. The business value is 187× compression on real robot data, search-without-decode on compressed motion streams, and a red-team-tested adversarial surface — delivered as a public PyPI package today.

## Technical Wedge

The technical edge is a frozen `wire-v1` motion transport codec with searchability built into the compressed format. Current evidence: **187.1345× compression** on `lerobot/columbia_cairlab_pusht_real`, benchmark gates B1/B2/B4/B5 pass, search-without-decode verified on the benchmark surface. Red-team attacks 1, 2, 6 withstood; attack 4 partially withstood. Strict bit-exact replay on `.zpbot` round-trip is not yet proven.

## Current Readiness

**`PUBLIC_PACKAGE_BUT_NOT_RELEASE_READY`** — The package is installable from PyPI (`pip install zpe-motion-kernel`). The engineering surface remains blocker-governed: B3 gate fails, red-team attacks 3 and 5 fail, and bit-exact replay is unproven.

## What Is Proved

- 187.1345× compression ratio on real robot data (lerobot benchmark)
- Benchmark gates B1, B2, B4, B5 pass
- Search-without-decode works on the benchmark surface
- Red-team attacks 1, 2, 6 fully withstood; attack 4 partially withstood
- Public PyPI package installs and runs cleanly

## What Is Not Being Claimed

- Full release readiness — engineering blockers remain active
- Bit-exact replay on `.zpbot` round-trip — not yet proven
- B3 benchmark gate — currently fails
- Red-team resilience on attacks 3, 5 — currently fail
- Rust ABI for robotics — no `.zpbot` Rust ABI is wired into this repo

## Ideal First Buyer

Robotics infrastructure team or simulation/replay platform seeking deterministic motion transport, compressed search, and audit-grade telemetry.

## Deployment Model

Public Python package — `pip install zpe-motion-kernel`. CLI via `zpe --version`. Source-available under SAL v6.0.

## Authority / Proof Anchors

| Anchor | Artifact |
|---|---|
| Benchmark gate verdicts | [`proofs/enterprise_benchmark/GATE_VERDICTS.json`](proofs/enterprise_benchmark/GATE_VERDICTS.json) |
| Red-team report | [`proofs/red_team/red_team_report.json`](proofs/red_team/red_team_report.json) |
| Engineering blockers | [`proofs/ENGINEERING_BLOCKERS.md`](proofs/ENGINEERING_BLOCKERS.md) |

## Role In The Zer0pa Family

ZPE-Robotics is a product-candidate member of the Zer0pa deterministic encoding family. [ZPE-IMC](https://github.com/Zer0pa/ZPE-IMC) is the umbrella integration and dispatch layer; this repo is the domain-specific robotics motion-transport wedge. IMC integration boundary is documented, not runtime-coupled.

---

<p>
  <img src=".github/assets/readme/section-bars/what-this-is.svg" alt="WHAT THIS IS" width="100%">
</p>

ZPE-Robotics is the public repository for the `zpe-motion-kernel` package.
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
| Package / import / CLI | `zpe-motion-kernel` / `zpe_robotics` / `zpe` |
| Acquisition surface | `pip install zpe-motion-kernel` |
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
- The current installable package artifact is `zpe-motion-kernel 0.1.0`, but
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
pip install zpe-motion-kernel
zpe --version
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
