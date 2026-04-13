# V6 Authority Surface — Completion Report

**Repo:** ZPE-Robotics
**Agent:** Codex GPT-5
**Date:** 2026-04-14
**Branch:** campaign/v6-authority-surface

## Dimensions Executed

- [x] **A: Key Metrics** — rewritten to the V6 Robotics slate with retained proof links
- [x] **B: Competitive Benchmarks** — added to `README.md` and expanded in `BENCHMARKS.md`
- [ ] **C: pip Install Fix** — skipped; root `pyproject.toml` already existed
- [x] **D: Publish Workflow** — consolidated to one workflow by keeping `publish.yml` and removing duplicate `release.yml`
- [ ] **E: Proof Sync** — N/A for Robotics

## Verification

- pip install from root: PASS
- import test: PASS
- Proof anchors verified: 4/4 exist
- Competitive claims honest: YES — only retained real-data compression wins are surfaced, and the `B3` failure remains explicit

## Key Metrics Written

| Metric | Value | Baseline | Proof File |
|--------|-------|----------|------------|
| COMPRESSION | 187.13× | vs zstd_l3 4.44× (42× better) | `proofs/enterprise_benchmark/benchmark_result.json`, `proofs/red_team/red_team_report.json` |
| ENCODE_P50 | 0.1106 ms | — | `proofs/enterprise_benchmark/benchmark_result.json` |
| DECODE_P50 | 0.0888 ms | — | `proofs/enterprise_benchmark/benchmark_result.json` |
| BENCHMARK_GATES | 4/5 pass | 3 datasets, 3 families | `proofs/enterprise_benchmark/GATE_VERDICTS.json`, `proofs/artifacts/lerobot_expanded_benchmarks/aggregate_spread_summary.json` |

## Issues / Blockers

- `main` had not yet incorporated the earlier V5 README truth sync, so the V6 README edit also carried those already-backed corrections forward to keep the front door internally consistent.
