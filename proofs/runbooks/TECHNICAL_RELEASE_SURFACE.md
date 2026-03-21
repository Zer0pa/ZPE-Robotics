# Technical Release Surface

Date: 2026-03-21
Repo: `ZPE-Robotics` current checkout

## Classification

This repo's truthful current public wedge is a standalone Python package:

- Repo: `ZPE-Robotics`
- Distribution: `zpe-motion-kernel`
- Import package: `zpe_robotics`
- CLI: `zpe`

It is not a full robotics-platform release surface, and it does not introduce a
runtime dependency on `ZPE-IMC`.

## Supported Install Surfaces

- Base user install:
  - `pip install zpe-motion-kernel`
- Repo-local development:
  - `pip install -e ".[dev]"`
- Benchmark and dataset tooling:
  - `pip install -e ".[benchmark]"`
- Telemetry sidecars:
  - `pip install -e ".[telemetry]"`
- Net-new dataset ingest tools:
  - `pip install -e ".[netnew]"`

Combined repo-local engineering surface when needed:

- `pip install -e ".[dev,benchmark,telemetry,netnew]"`

## Dependency Truth

- Base runtime dependencies stay narrow: `numpy`, `mcap`
- Comet and Opik remain optional sidecars under `telemetry`
- Enterprise benchmark dependencies remain optional under `benchmark`
- No IMC runtime import is introduced by this repo

## Workflow Truth

- Trusted publishing remains OIDC-based in `.github/workflows/publish.yml`
- Workflow surfaces that use `uv` now sync against the declared `dev` extra
  with lock enforcement:
  - `uv sync --frozen --extra dev`
- Test CI covers Linux x86 on Python `3.11` and `3.12`

## Verification Anchors

- Clean-clone source install:
  `proofs/artifacts/operations/20260321T203557Z_tech_alignment_clean_clone_result.json`
- Verification summary:
  `proofs/artifacts/operations/20260321T203557Z_technical_alignment_verification.md`
