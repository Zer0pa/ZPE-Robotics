<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-Robotics Masthead" width="100%">
</p>

# Auditor Playbook

<p>
  <img src="../.github/assets/readme/section-bars/what-this-is.svg" alt="WHAT THIS IS" width="100%">
</p>

This is the shortest verification path anchored to current authority.
Engineering is not complete. Local green slices do not override the March 21
blocker-state evidence.
The repo is public and the package is published, but those facts are
non-sovereign versus the blocker files below.

<p>
  <img src="../.github/assets/readme/section-bars/quick-start.svg" alt="QUICK START" width="100%">
</p>

| Surface | Current truth |
|---|---|
| Repo scope | standalone Python package wedge |
| Repo visibility | public GitHub repo and public package surface |
| Current authority | `../proofs/ENGINEERING_BLOCKERS.md` |
| Benchmark gates | `B1`, `B2`, `B4`, `B5` pass; `B3` fails |
| Narrow claim gate | bounded-lossy archive/search passes only for the ratified surface |
| Red-team | attacks `1`, `2`, `5`, and `6` withstand; attack `3` fails; attack `4` partially withstands; attack `7` remains open |
| Runtime boundary | no robotics `.zpbot` Rust ABI is wired into this repo |
| Release-ready verdict | not authorized |

<p>
  <img src="../.github/assets/readme/section-bars/verification.svg" alt="VERIFICATION" width="100%">
</p>

1. Inspect the current authority files first:

```bash
sed -n '1,220p' ../proofs/ENGINEERING_BLOCKERS.md
cat ../proofs/enterprise_benchmark/GATE_VERDICTS.json
cat ../proofs/red_team/red_team_report.json
cat ../proofs/narrow_claim/NARROW_CLAIM_GATE.json
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
zpe-robotics --version
```

4. Verify the packet and CLI surface:

```bash
zpe-robotics verify ../proofs/release_candidate/canonical_release_packet.zpbot
zpe-robotics info ../proofs/release_candidate/canonical_release_packet.zpbot
```

5. If you need a release-workflow check, compare:

- `.github/workflows/publish.yml`
- `../proofs/runbooks/TRUSTED_PUBLISHING_OPERATOR_STEPS.md`

<p>
  <img src="../.github/assets/readme/section-bars/evidence.svg" alt="EVIDENCE" width="100%">
</p>

Read these together:

- `../proofs/ENGINEERING_BLOCKERS.md`
- `../proofs/narrow_claim/NARROW_CLAIM_GATE.json`
- `../proofs/enterprise_benchmark/GATE_VERDICTS.json`
- `../proofs/red_team/red_team_report.json`
- `../proofs/runbooks/TECHNICAL_RELEASE_SURFACE.md`
- `../proofs/imc_audit/imc_architecture_audit.json`

Treat these as historical or supporting only:

- `../proofs/FINAL_STATUS.md`
- `../proofs/artifacts/historical/README.md`

<p>
  <img src="../.github/assets/readme/section-bars/where-to-go.svg" alt="WHERE TO GO" width="100%">
</p>

If your replay or reading disagrees with the current authority:

- capture the commit SHA
- capture the exact commands
- retain stdout and stderr
- save the produced artifact directory
- record the mismatch instead of narrating around it
