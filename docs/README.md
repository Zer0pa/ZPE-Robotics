<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-Robotics Masthead" width="100%">
</p>

# Docs Index

This directory routes readers to the smallest truthful doc for the current
ZPE-Robotics surface.

<p>
  <img src="../.github/assets/readme/section-bars/faq-and-support.svg" alt="FAQ AND SUPPORT" width="100%">
</p>

| Document | What it is |
|---|---|
| `FAQ.md` | short answers on blocker state, package availability, and current proof boundaries |
| `AUDITOR_PLAYBOOK.md` | shortest outsider verification route for the blocker-governed surface |
| `PUBLIC_AUDIT_LIMITS.md` | honesty boundary for what public artifacts do and do not prove |
| `SUPPORT.md` | support routing, escalation paths, and response expectations |

<p>
  <img src="../.github/assets/readme/section-bars/interface-contracts.svg" alt="INTERFACE CONTRACTS" width="100%">
</p>

| Document | What it is |
|---|---|
| `ZPBOT_V2_AUTHORITY_SURFACE.md` | packet-contract reference for the `zpbot-v2` authority surface |
| `family/ROBOTICS_RELEASE_LINKAGE.md` | docs linkage to `ZPE-IMC` and explicit non-runtime-coupling boundary |
| `ARCHITECTURE.md` | runtime, proof, and package-surface map for the standalone robotics package |

If you need packet or IMC linkage truth, start with the two files above before
reading supporting prose.

<p>
  <img src="../.github/assets/readme/section-bars/release-notes.svg" alt="RELEASE NOTES" width="100%">
</p>

| Document | What it is |
|---|---|
| `../README.md` | front door for current public truth and route-out links |
| `../proofs/runbooks/TECHNICAL_RELEASE_SURFACE.md` | release gate, operator boundary, and publish workflow routing |
| `RELEASE_CANDIDATE.md` | March 18 release-candidate note preserved as non-governing context |
| `../CHANGELOG.md` | release-surface deltas and docs-surface additions |

<p>
  <img src="../.github/assets/readme/section-bars/family-alignment.svg" alt="FAMILY ALIGNMENT" width="100%">
</p>

| Workstream | Relation | Anchor |
|---|---|---|
| `ZPE-IMC` | docs-layout and release-hygiene reference model | `family/ROBOTICS_RELEASE_LINKAGE.md` |
| `ZPE-Robotics` | current standalone package workstream | `../README.md`, `ARCHITECTURE.md` |

<p>
  <img src="../.github/assets/readme/section-bars/proof-corpus.svg" alt="PROOF CORPUS" width="100%">
</p>

| Document | What it is |
|---|---|
| `../proofs/ENGINEERING_BLOCKERS.md` | governing blocker proof and current engineering truth |
| `../proofs/enterprise_benchmark/GATE_VERDICTS.json` | benchmark gate pass/fail record |
| `../proofs/red_team/red_team_report.json` | adversarial verdicts and open failures |
| `../proofs/artifacts/historical/README.md` | historical lineage index, not current authority |

<p>
  <img src="../.github/assets/readme/section-bars/engineering-references.svg" alt="ENGINEERING REFERENCES" width="100%">
</p>

Use these stable references when you need the current engineering boundary:

- `../proofs/runbooks/TECHNICAL_RELEASE_SURFACE.md`
- `../proofs/runbooks/TRUSTED_PUBLISHING_OPERATOR_STEPS.md`
- `OPERATOR_RUNBOOK.md`
- `DOC_REGISTRY.md`
- `LEGAL_BOUNDARIES.md`

<p>
  <img src="../.github/assets/readme/section-bars/what-this-directory-is-not.svg" alt="WHAT THIS DIRECTORY IS NOT" width="100%">
</p>

This directory does not contain:

- the governing blocker proof itself, which lives under `../proofs/`
- package implementation details, which live under `../src/`
- historical bundles that should be treated as current authority
