# BENCHMARKS

This file is the competitive benchmark front door for ZPE-Robotics.

The governing comparison surface is the retained real-data LeRobot benchmark on
`columbia_cairlab_pusht_real` with `136` episodes and `27,808` frames. The
headline result is a compression ratio of `187.1345029239766×` for `zpe_p8`
from [`proofs/enterprise_benchmark/benchmark_result.json`](proofs/enterprise_benchmark/benchmark_result.json).

Two constraints stay in force:

- `B3` remains FAIL in [`proofs/enterprise_benchmark/GATE_VERDICTS.json`](proofs/enterprise_benchmark/GATE_VERDICTS.json), so this is not a lossless claim.
- Red-team attack `attack_1_strawman_baseline` in [`proofs/red_team/red_team_report.json`](proofs/red_team/red_team_report.json) WITHSTANDS and records ZPE as `42.14035087719298×` better than `zstd_l3` on the governing real dataset.

## Compression Benchmarks

| Tool | Compression Ratio | Notes |
|------|-------------------|-------|
| **ZPE P8** | **187.13×** | searchable without decode; bit-exact replay not proven |
| zstd_l19 | 4.59× | strongest retained classical compressor in the benchmark set |
| zstd_l3 | 4.44× | red-team stress baseline |
| mcap_zstd | 3.99× | MCAP + zstd container baseline |
| gzip_l9 | 3.97× | retained gzip baseline |
| lz4_default | 3.00× | low-latency baseline |
| mcap_lz4 | 2.79× | MCAP + lz4 container baseline |
| h5py_gzip9 | 2.69× | HDF5 gzip baseline |
| h5py_lzf | 2.15× | HDF5 fast baseline |

## Source Files

- [`proofs/enterprise_benchmark/benchmark_result.json`](proofs/enterprise_benchmark/benchmark_result.json)
- [`proofs/enterprise_benchmark/GATE_VERDICTS.json`](proofs/enterprise_benchmark/GATE_VERDICTS.json)
- [`proofs/red_team/red_team_report.json`](proofs/red_team/red_team_report.json)
- [`.github/workflows/e_g3_comparator.yml`](.github/workflows/e_g3_comparator.yml)
