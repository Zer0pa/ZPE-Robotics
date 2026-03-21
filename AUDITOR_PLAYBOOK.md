<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-Robotics Masthead" width="100%">
</p>

# Auditor Playbook

<p>
  <img src=".github/assets/readme/section-bars/what-this-is.svg" alt="WHAT THIS IS" width="100%">
</p>

This is the shortest honest verification path for the current ZPE-Robotics
workstream repo. Overall engineering state is not complete. Gate-local green
slices remain subordinate to the March 21 blocker-state evidence.

<p>
  <img src=".github/assets/readme/section-bars/quick-start.svg" alt="QUICK START" width="100%">
</p>

| Surface | Current truth |
|---|---|
| Repo scope | standalone Python package wedge |
| Current authority | `proofs/ENGINEERING_BLOCKERS.md` |
| Benchmark gates | `B1`, `B2`, `B4`, `B5` pass; `B3` fails |
| Red-team | attacks `3` and `5` fail; attack `4` partially withstands |
| Runtime boundary | no robotics `.zpbot` Rust ABI is wired into this repo |
| Public release | not authorized |

<p>
  <img src=".github/assets/readme/section-bars/verification.svg" alt="VERIFICATION" width="100%">
</p>

1. Inspect the current authority files first:

```bash
sed -n '1,220p' proofs/ENGINEERING_BLOCKERS.md
cat proofs/enterprise_benchmark/GATE_VERDICTS.json
cat proofs/red_team/red_team_report.json
```

2. Create an environment and install the repo-local engineering surface:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[dev,benchmark,telemetry,netnew]"
```

3. Run the current test surface:

```bash
python -m pytest tests -q
python -m build
zpe --version
```

4. Verify the packet and CLI surface:

```bash
zpe verify proofs/release_candidate/canonical_release_packet.zpbot
zpe info proofs/release_candidate/canonical_release_packet.zpbot
```

5. If you need a release-workflow check, compare:

- `.github/workflows/publish.yml`
- `proofs/runbooks/TRUSTED_PUBLISHING_OPERATOR_STEPS.md`

<p>
  <img src=".github/assets/readme/section-bars/evidence.svg" alt="EVIDENCE" width="100%">
</p>

Read these together:

- `proofs/ENGINEERING_BLOCKERS.md`
- `proofs/enterprise_benchmark/GATE_VERDICTS.json`
- `proofs/red_team/red_team_report.json`
- `proofs/runbooks/TECHNICAL_RELEASE_SURFACE.md`
- `proofs/imc_audit/imc_architecture_audit.json`

Treat these as historical or supporting only:

- `proofs/FINAL_STATUS.md`
- `proofs/CONSOLIDATED_PROOF_REPORT.md`
- `proofs/logs/PRE_REPO_AUTHORITY_SNAPSHOT_2026-03-09.md`

<p>
  <img src=".github/assets/readme/section-bars/where-to-go.svg" alt="WHERE TO GO" width="100%">
</p>

If your replay or reading disagrees with the current authority:

- capture the commit SHA
- capture the exact commands
- retain stdout and stderr
- save the produced artifact directory
- record the mismatch instead of narrating around it
