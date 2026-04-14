# Proof Lineage Paths

Some frozen proof artifacts in this repo still contain:

- absolute development paths such as `...`
- the older package name `zpe-motion-kernel`
- the older CLI name `zpe`

Those residues are preserved intentionally in historical artifacts. They record
the point-in-time environment under which the evidence was generated. They do
not control the current package, CLI, or release status.

Why these files are not mass-edited:

- frozen proof bundles are part of the evidence chain
- rewriting them for cosmetic cleanup would blur provenance
- the active authority surface already states the current package identity and
  blocker state directly

Current authority files that outrank historical residue:

- `README.md`
- `pyproject.toml`
- `docs/OPERATOR_RUNBOOK.md`
- `docs/RELEASE_CANDIDATE.md`
- `proofs/ENGINEERING_BLOCKERS.md`
- `proofs/enterprise_benchmark/GATE_VERDICTS.json`
- `proofs/red_team/red_team_report.json`

Use those files for the live package / import / CLI identity and the current
engineering boundary. Treat older names inside frozen proofs as lineage only.
