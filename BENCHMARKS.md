# Benchmarks

This document indexes the checked-in benchmark surfaces for `zpe-robotics`.
It is evidence-bound. It does not close `B3`, red-team attack `3`, or the
governing red-team attack `5` artifact on its own.

## Methodology

- Public real-data source: LeRobot dataset repositories on Hugging Face.
- Acquisition path: `python scripts/acquire_enterprise_dataset.py ...`
- Benchmark engine: `python scripts/enterprise_benchmark.py ...`
- Expanded sweep engine: `python scripts/lerobot_benchmark_sweep.py ...`
- Sample mode: `episode_window`
- Target frames: `1000`
- Runs per comparator in the expanded sweep artifacts: `20`
- Published baselines in proof artifacts: raw float32, `gzip -9`, `lz4`, `zstd_l3`, `zstd_l19`, `mcap_lz4`, `mcap_zstd`, `h5py_gzip9`, `h5py_lzf`
- Scope note: `proofs/artifacts/lerobot_expanded_benchmarks/aggregate_spread_summary.json` is benchmark breadth evidence, not blocker closure

## Reproduction Commands

```bash
python scripts/acquire_enterprise_dataset.py --repo-id lerobot/columbia_cairlab_pusht_real --data-root ./benchmark_data --output ./benchmark_data/pusht_real_provenance.json --include-namespace --require-real
python scripts/enterprise_benchmark.py --dataset-root ./benchmark_data/lerobot__columbia_cairlab_pusht_real --dataset-name lerobot/columbia_cairlab_pusht_real --dataset-provenance ./benchmark_data/pusht_real_provenance.json --output-dir ./benchmark_output/pusht_real --runs 20 --target-frames 1000 --sample-mode episode_window
python scripts/lerobot_benchmark_sweep.py --data-root ./benchmark_data --output-dir ./benchmark_output/expanded --require-real --runs 20 --target-frames 1000
```

## Current Anchor Table

| dataset | baseline | ZPE | ratio | improvement |
|---|---|---|---:|---:|
| `lerobot/columbia_cairlab_pusht_real` | `zstd_l19 13.03x` | `zpe_p8 186.05x` | `186.05x` | `14.27x vs zstd_l19` |

## Source Artifacts

- `proofs/enterprise_benchmark/benchmark_result.json`
- `proofs/enterprise_benchmark/GATE_VERDICTS.json`
- `proofs/artifacts/lerobot_expanded_benchmarks/aggregate_spread_summary.json`
- `proofs/artifacts/lerobot_expanded_benchmarks/dataset_manifest.json`
