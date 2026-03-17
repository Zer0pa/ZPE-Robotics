# FAQ

## Is this repo launch-ready?

No. The current pre-repo authority snapshot is `NO-GO`.

## What blocks launch right now?

`E-G3`, plus Phase 5 clean-clone verification.

## Why keep the February bundles if they are stale?

They are proof lineage. They show how the sector reached its current state and
what changed, but they are not the current authority surface.

## Where is the current authority?

For this staged repo, the current truth is summarized in
`proofs/logs/PRE_REPO_AUTHORITY_SNAPSHOT_2026-03-09.md`. A repo-root rerun is
still required.

## How is Robotics related to IMC?

IMC is the repo-structure model and release-linkage reference, not a shared
runtime dependency that this repo currently imports.

## Why is this repo private?

Phase 3 and Phase 4 are private staging only. No public release action is
allowed until a later explicit gate.
