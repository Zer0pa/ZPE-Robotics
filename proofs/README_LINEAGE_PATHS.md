# Proof Lineage Paths

This note explains path and name residue in frozen proof artifacts. It is an
authority-routing document, not a rewrite permission slip.

## Current Authority

Use these files for current ZPE-Robotics status:

- `proofs/ENGINEERING_BLOCKERS.md`
- `proofs/enterprise_benchmark/GATE_VERDICTS.json`
- `proofs/red_team/red_team_report.json`
- `proofs/release_candidate/anomaly_detection_result.json`
- `proofs/release_candidate/anomaly_threshold_sweep.json`
- `proofs/artifacts/lerobot_expanded_benchmarks/aggregate_spread_summary.json`
- `proofs/imc_audit/imc_architecture_audit.json`

Runtime and proof artifacts outrank prose. Historical bundles do not override
the current blocker surface.

## Historical Residue

Some proof bundles preserve absolute local paths, old package names, temporary
workspace paths, and prior release-candidate labels. Those strings are lineage
metadata from the machine and phase that produced the artifact. They should not
be mass-edited for aesthetics because doing so would weaken provenance.

When a historical path disagrees with the current repository layout, resolve it
by using the current authority list above and the active repository root:

`/Users/Zer0pa/ZPE/ZPE Robotics/zpe-robotics`

## Non-Claims

This lineage note does not close:

- benchmark gate `B3`
- red-team attack `3`
- ZPE-IMC Robotics Rust ABI routing
- red-team attack `7` external reproduction

Attack `5` is not closed by this note. Its current blocker-facing status comes
from the live red-team and anomaly artifacts at threshold `3.22`, with
`false_positive_rate=0.05` and `recall=0.9` on the declared Phase 10 holdout
surface.
