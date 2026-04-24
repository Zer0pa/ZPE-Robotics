# Governance

## Authority Order

For ZPE-Robotics, current authority resolves in this order:

1. Committed proof artifacts under `proofs/`.
2. Tests and executable verification scripts.
3. README and docs prose.
4. Historical bundles under `proofs/artifacts/historical/`.

If these disagree, the active proof artifacts win. Historical proof bundles are
lineage only and do not override current blocker-state evidence.

## Claim Policy

- Keep claims scoped to this robotics package.
- Do not inherit release readiness, benchmark verdicts, or runtime claims from
  ZPE-IMC or any other ZPE product.
- Do not close a blocker through narrative; close it with rerun evidence or a
  clearly ratified replacement gate.
- Keep `README.md` Commercial Readiness `Verdict` within the parser enum.

## Change Control

Pull requests require owner review and are not self-merged by automation agents.
Changes to release authority, blocker status, or proof anchors must name the
evidence file that justifies the change.
