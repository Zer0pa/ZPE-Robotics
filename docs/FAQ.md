# FAQ

## Is this repo launch-ready?

No. The current release-candidate kernel gate and clean-clone verification are `GO`, but public launch is still not complete.

## What blocks launch right now?

Explicit public-release staging and distribution decisions. The old `E-G3` blocker and clean-clone gate are closed.

## Why keep the February bundles if they are stale?

They are proof lineage. They show how the sector reached its current state and
what changed, but they are not the current authority surface.

## Where is the current authority?

For this staged repo, the current release-candidate truth is summarized in
`proofs/FINAL_STATUS.md`, `proofs/CONSOLIDATED_PROOF_REPORT.md`, and the hosted
artifacts under `proofs/release_candidate/`, including
`clean_clone_result.json`. The March 9 snapshot remains lineage, not the
current gate result.

## How is Robotics related to IMC?

IMC is the repo-structure model and release-linkage reference, not a shared
runtime dependency that this repo currently imports.

## Why is this repo private?

Phase 3 and Phase 4 are private staging only. No public release action is
allowed until a later explicit gate.
