# Docs Alignment Execution Plan

Date: 2026-03-21
Repo: /Users/Zer0pa/ZPE/ZPE Robotics/zpe-robotics
Authority playbook: /Users/Zer0pa/ZPE/ZPE Robotics/zpe-robotics/proofs/runbooks/ZER0PA_REPO_DOCS_PLAYBOOK_CANONICAL_2026-03-21.md

## Governing Objective

Bring the repository documentation surface into enterprise-grade alignment with
the repo's actual March 21 truth, without inheriting claims from ZPE-IMC that
this repo has not proven.

## Working Truth

- Public wedge: standalone Python package `zpe-motion-kernel`
- Import package: `zpe_robotics`
- CLI: `zpe`
- Technical release surface: aligned for build/install/release verification
- Engineering completion: not achieved
- Governing blockers:
  - benchmark gate `B3` failed
  - red-team attacks `3` and `5` failed
  - red-team attack `4` partially withstood
  - external reproduction remains open
  - `.zpbot` encode/decode is not routed through ZPE-IMC Rust

## File Ownership

- Main agent: all repo file edits in this pass
- Subagents: review memos only, no file edits

## Execution Steps

1. Copy the canonical docs playbook and shared render assets into the repo.
2. Replace stale `GO` and clean-clone-forward authority language with the March
   21 blocker-state evidence surface.
3. Establish one canonical README authority block and route supporting concerns
   into dedicated docs.
4. Add missing support, governance, releasing, citation, and doc-registry files.
5. Preserve GitHub-safe layout using the shared masthead, section bars, and
   flat scan-first tables.
6. Run a falsification pass against claims, links, asset paths, and live/local
   sync.
7. Write a repo-local falsification artifact and a standard work receipt.
