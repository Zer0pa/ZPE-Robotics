# Benchmarks

This document indexes the checked-in benchmark surfaces for `zpe-robotics`.
It is evidence-bound. It does not close `B3`, red-team attack `3`, or the
governing red-team attack `5` artifact on its own.

## Methodology

- Public real-data source: LeRobot dataset repositories on Hugging Face.
- Acquisition path: `python scripts/acquire_enterprise_dataset.py ...`
- Benchmark engine: `python scripts/enterprise_benchmark.py ...`
- Expanded sweep engine: `python scripts/lerobot_benchmark_sweep.py ...`
- Sample mode on the expanded sweep artifacts: `episode_window`
- Target frames on the expanded sweep artifacts: `1000`
- Runs per comparator in the expanded sweep artifacts: `20`
- Published baselines in proof artifacts: raw float32, `gzip -9`, `lz4`, `zstd_l3`, `zstd_l19`, `mcap_lz4`, `mcap_zstd`, `h5py_gzip9`, `h5py_lzf`
- Scope note: `proofs/artifacts/lerobot_expanded_benchmarks/aggregate_spread_summary.json` is benchmark breadth evidence, not blocker closure

## Reproduction Commands

```bash
python scripts/acquire_enterprise_dataset.py --repo-id lerobot/columbia_cairlab_pusht_real --data-root ./benchmark_data --output ./benchmark_data/pusht_real_provenance.json --include-namespace --require-real
python scripts/enterprise_benchmark.py --dataset-root ./benchmark_data/lerobot__columbia_cairlab_pusht_real --dataset-name lerobot/columbia_cairlab_pusht_real --dataset-provenance ./benchmark_data/pusht_real_provenance.json --output-dir ./benchmark_output/pusht_real --runs 20 --target-frames 1000 --sample-mode episode_window
python scripts/lerobot_benchmark_sweep.py --data-root ./benchmark_data --output-dir ./benchmark_output/expanded --require-real --runs 20 --target-frames 1000
python scripts/rosbag_demo_benchmark.py --output proofs/artifacts/benchmarks/rosbag_demo_benchmark.json
```

## Published Summary

| dataset | baseline | ZPE | ratio | improvement |
|---|---|---|---:|---:|
| `lerobot/columbia_cairlab_pusht_real` | `zstd_l19 13.03x` | `zpe_p8 186.05x` | `186.05x` | `14.27x vs zstd_l19` |
| `lerobot/aloha_mobile_shrimp` | `zstd_l19 3.55x` | `zpe_p8 61.27x` | `61.27x` | `17.28x vs zstd_l19` |
| `lerobot/umi_cup_in_the_wild` | `zstd_l19 1.08x` | `zpe_p8 58.70x` | `58.70x` | `54.12x vs zstd_l19` |
| `deterministic_rosbag2_demo_fixture` | `native_mcap 8.59x` | `zpbot_packet_library 14.88x` | `14.88x` | `1.73x vs native_mcap` |

## LeRobot Real-Data Detail

| dataset | revision | sample_mode | target_frames | episode_count_used | raw_size | zstd_l19 | lz4 | ZPE | max_abs_error | encode_p50_ms | decode_p50_ms |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `lerobot/columbia_cairlab_pusht_real` | `66482aa15878b5362c98620f7f60ee23ef1d5a2c` | `episode_window` | `1000` | `1` | `32000 B` | `13.03x` | `8.31x` | `186.05x` | `0.253527` | `0.074684` | `0.056404` |
| `lerobot/aloha_mobile_shrimp` | `6e828202059d2cc204b61ff968c232d202127a34` | `episode_window` | `1000` | `1` | `56000 B` | `3.55x` | `2.17x` | `61.27x` | `0.726666` | `0.115269` | `0.087769` |
| `lerobot/umi_cup_in_the_wild` | `c16ab60ce0862c60a6c83c200d050b4013af3333` | `episode_window` | `1000` | `1` | `28000 B` | `1.08x` | `1.00x` | `58.70x` | `0.265393` | `0.072549` | `0.054044` |

## Rosbag2-Style Demo Detail

| dataset | raw_size | legacy_bag | native_mcap | zstd_l19 | lz4 | zpbot_packet_library | improvement |
|---|---:|---:|---:|---:|---:|---:|---:|
| `deterministic_rosbag2_demo_fixture` | `73728 B` | `7.70x` | `8.59x` | `1.09x` | `1.00x` | `14.88x` | `1.73x vs native_mcap` |

Source: `proofs/artifacts/benchmarks/rosbag_demo_benchmark.json`

## Qualification Misses

| dataset | status | reason |
|---|---|---|
| `lerobot/pusht_image` | skipped | `INSUFFICIENT_JOINT_DIM_LT_6` |

## Open Gate Context

- `B3` still fails in `proofs/enterprise_benchmark/GATE_VERDICTS.json`.
- Red-team attack `3` still fails in `proofs/red_team/red_team_report.json`.
- The anomaly threshold source is aligned in code, but the governing red-team attack `5` artifact has not been regenerated in this document set.

## Source Artifacts

- `proofs/enterprise_benchmark/benchmark_result.json`
- `proofs/enterprise_benchmark/GATE_VERDICTS.json`
- `proofs/red_team/red_team_report.json`
- `proofs/artifacts/lerobot_expanded_benchmarks/aggregate_spread_summary.json`
- `proofs/artifacts/lerobot_expanded_benchmarks/dataset_manifest.json`
- `proofs/artifacts/lerobot_expanded_benchmarks/lerobot__columbia_cairlab_pusht_real/benchmark_result.json`
- `proofs/artifacts/lerobot_expanded_benchmarks/lerobot__aloha_mobile_shrimp/benchmark_result.json`
- `proofs/artifacts/lerobot_expanded_benchmarks/lerobot__umi_cup_in_the_wild/benchmark_result.json`
- `proofs/artifacts/benchmarks/rosbag_demo_benchmark.json`
