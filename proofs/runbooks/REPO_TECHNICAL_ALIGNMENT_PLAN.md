# Repo Technical Alignment Plan

Date: 2026-03-21
Repo: ./zpe-robotics
Scope: technical release-architecture alignment pass for the current public wedge

## Objective

Align the repo's technical release surface with its truthful current architecture:
the installable Python package `zpe-robotics`, its CLI, its optional probe
and telemetry extras, and its static release workflows.

## Plan

1. Inspect the actual package/runtime/release shape:
   - `pyproject.toml`
   - import package layout under `src/`
   - CLI entry points
   - workflow files under `.github/workflows/`
   - verification scripts and tests
2. Classify the truthful target architecture for this repo and identify drift:
   - naming mismatches
   - undeclared or mis-scoped dependencies
   - optional extras that should not be base runtime deps
   - release workflow contradictions
3. Implement the minimum technically correct fixes inside this repo only.
4. Falsify the result by building, installing, importing, running targeted CLI
   and test paths, and statically checking release workflow logic.
5. Write a receipt with evidence paths and the truthful verdict for the current
   release-alignment gate.
