<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-Robotics Masthead" width="100%">
</p>

# Governance

<p>
  <img src=".github/assets/readme/section-bars/what-this-is.svg" alt="WHAT THIS IS" width="100%">
</p>

This document defines the claim, evidence, and release-language boundary for
the ZPE-Robotics workstream repo.

| Canonical anchor | Value |
|---|---|
| Repository | `https://github.com/Zer0pa/ZPE-Robotics.git` |
| Package | `zpe-robotics` |
| Contact | `architects@zer0pa.ai` |

<p>
  <img src=".github/assets/readme/section-bars/evidence-and-claims.svg" alt="EVIDENCE AND CLAIMS" width="100%">
</p>

| Rule | Current policy | Authority |
|---|---|---|
| Source of truth | repo proof artifacts outrank prose | `proofs/ENGINEERING_BLOCKERS.md` |
| Gate language | `GO` and `NO-GO` apply only to named gates, not to the whole repo by implication | `proofs/enterprise_benchmark/GATE_VERDICTS.json` |
| Historical evidence | historical bundles remain lineage only | `proofs/artifacts/historical/README.md` |
| Release status | package availability does not equal engineering completion | `RELEASING.md`, `proofs/ENGINEERING_BLOCKERS.md` |
| Runtime coupling | do not claim current IMC runtime routing | `proofs/imc_audit/imc_architecture_audit.json` |
| Falsification discipline | mixed evidence stays visible; it is not rewritten into a pass | `proofs/red_team/red_team_report.json` |

<p>
  <img src=".github/assets/readme/section-bars/compatibility-commitments.svg" alt="COMPATIBILITY COMMITMENTS" width="100%">
</p>

| Coordinate | Current lock |
|---|---|
| Repo role | private workstream repo |
| Public wedge | standalone Python package |
| Distribution / import / CLI | `zpe-robotics` / `zpe_robotics` / `zpe-robotics` |
| Runtime coupling to `ZPE-IMC` | none |
| Packet-contract reference | `docs/ZPBOT_V2_AUTHORITY_SURFACE.md` |
| License identity | `LicenseRef-Zer0pa-SAL-6.0` |

<p>
  <img src=".github/assets/readme/section-bars/summary.svg" alt="SUMMARY" width="100%">
</p>

- `current truth`: backed by the current authority files
- `supporting`: useful context that does not override the authority files
- `historical`: preserved lineage only
- `operator-only`: requires credentials, payment, UI access, or other outside control

<p>
  <img src=".github/assets/readme/section-bars/escalation-path.svg" alt="ESCALATION PATH" width="100%">
</p>

Owner decisions still outside repo-local execution:

- public-release authorization
- PyPI Trusted Publishing UI registration
- any decision to reopen the Rust-routing lane instead of keeping the current
  no-IMC-runtime boundary
