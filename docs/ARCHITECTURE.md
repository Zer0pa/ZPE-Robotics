<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-Robotics Masthead" width="100%">
</p>

# Architecture

<p>
  <img src="../.github/assets/readme/section-bars/what-this-is.svg" alt="WHAT THIS IS" width="100%">
</p>

This doc maps the runtime and proof surface for the current standalone
`zpe-robotics` package wedge.

<p>
  <img src="../.github/assets/readme/section-bars/repo-shape.svg" alt="REPO SHAPE" width="100%">
</p>

| Path | Purpose |
|---|---|
| `src/zpe_robotics/` | installable package, CLI, packet, and evaluation logic |
| `tests/` | release-surface, CLI, codec, and regression checks |
| `scripts/` | replay, benchmark, clean-clone, and falsification helpers |
| `docs/` | front-door, support, legal, and linkage docs |
| `proofs/` | blockers, benchmark artifacts, red-team outputs, runbooks, and history |

<p>
  <img src="../.github/assets/readme/section-bars/architecture-and-theory.svg" alt="ARCHITECTURE AND THEORY" width="100%">
</p>

| Surface | Files | Responsibility |
|---|---|---|
| core packet path | `codec.py`, `wire.py`, `release_candidate.py` | `.zpbot` encode/decode, packet parsing, and release defaults |
| CLI and audit | `cli.py`, `audit_bundle.py` | installable command surface and audit artifact generation |
| bag and dataset adapters | `rosbag_adapter.py`, `lerobot_codec.py`, `mcap_bridge.py`, `enterprise_dataset.py` | bag IO, LeRobot compression, and benchmark dataset access |
| search and token surfaces | `primitive_index.py`, `primitives.py`, `vla_bridge.py`, `anomaly.py` | 8-direction x 3-magnitude tokenization for primitive search, FAST export, and anomaly scoring |
| evaluation and falsification | `kinematics.py`, `vla_eval.py`, `falsification.py`, `determinism.py` | fidelity, token-quality evaluation, falsification, and replay checks |
| support utilities | `constants.py`, `runtime_probe.py`, `telemetry.py`, `utils.py` | thresholds, probes, telemetry hooks, and helpers |

<p>
  <img src="../.github/assets/readme/section-bars/interface-contracts.svg" alt="INTERFACE CONTRACTS" width="100%">
</p>

| Contract | Current truth | Authority |
|---|---|---|
| distribution surface | `zpe-robotics` / `zpe_robotics` / `zpe-robotics` | `../pyproject.toml` |
| packet-contract reference | frozen `zpbot-v2` / `wire-v1` surface | `ZPBOT_V2_AUTHORITY_SURFACE.md` |
| runtime dependency boundary | runtime deps are `numpy` and `mcap`; extras remain optional | `../pyproject.toml`, `../proofs/runbooks/TECHNICAL_RELEASE_SURFACE.md` |
| primitive scope | 8-direction x 3-magnitude tokens power search and FAST export only; the wire codec itself is FFT+zlib | `../src/zpe_robotics/primitives.py`, `../src/zpe_robotics/primitive_index.py`, `../src/zpe_robotics/vla_bridge.py` |
| IMC boundary | No IMC runtime import is introduced by this repo | `../proofs/runbooks/TECHNICAL_RELEASE_SURFACE.md`, `../proofs/imc_audit/imc_architecture_audit.json` |

<p>
  <img src="../.github/assets/readme/section-bars/verification.svg" alt="VERIFICATION" width="100%">
</p>

| Evidence surface | What it currently proves |
|---|---|
| `../proofs/ENGINEERING_BLOCKERS.md` | governing blocker-state and completion boundary |
| `../proofs/enterprise_benchmark/GATE_VERDICTS.json` | benchmark gate results |
| `../proofs/red_team/red_team_report.json` | adversarial findings and open provenance boundary |
| `../proofs/runbooks/TECHNICAL_RELEASE_SURFACE.md` | package/runtime/release classification |
| `../proofs/artifacts/historical/README.md` | historical lineage and preservation rules |

Common execution path:

- `python -m pytest tests -q`
- `python -m build`
- `zpe-robotics verify proofs/release_candidate/canonical_release_packet.zpbot`
