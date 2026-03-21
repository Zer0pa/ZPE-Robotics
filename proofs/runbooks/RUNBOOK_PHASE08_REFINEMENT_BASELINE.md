# RUNBOOK: Phase 8 Refinement Baseline

## Purpose

Benchmark the current first-lane artifact paths on a clean environment so Phase 8 can decide whether any path deserves deeper optimization or a Rust move.

## Inputs

- `proofs/release_candidate/canonical_release_packet.zpbot`
- `scripts/benchmark_phase8_core_paths.py`

## Preferred Surface

Use RunPod or another clean environment for this benchmark so the Mac stays lean. Record pod disk status before and after heavy work.

## Command

```bash
PYTHONPATH=src python3 scripts/benchmark_phase8_core_paths.py \
  proofs/release_candidate/canonical_release_packet.zpbot \
  proofs/refinement/phase08_baseline_perf.json
```

## Expected Output

- `proofs/refinement/phase08_baseline_perf.json`

The JSON must include:

- environment metadata
- packet metadata and decoded shape
- median and p95 timings for `describe_packet`, `decode_packet`, `encode_packet`, `build_provenance_manifest`, and `generate_audit_bundle`
- a ranking of paths by median latency

## Pass Condition

- The benchmark runs on a clean environment without mutating packet semantics.
- The output artifact is committed or otherwise preserved as the refinement baseline.
- The follow-on verdict names a measured hot path or explicitly rejects migration.

## Non-Claims

- This benchmark is not first-lane closure evidence.
- This benchmark does not by itself justify a Rust migration.
- This benchmark does not imply Jetson, real-time control-loop, or certification readiness.
