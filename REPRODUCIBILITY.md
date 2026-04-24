# Reproducibility

## Canonical Inputs

- `proofs/release_candidate/canonical_release_packet.zpbot`
- `proofs/enterprise_benchmark/dataset_provenance.json`
- `proofs/artifacts/lerobot_expanded_benchmarks/dataset_manifest.json`
- `proofs/release_candidate/anomaly_detection_result.json`
- `proofs/release_candidate/anomaly_threshold_sweep.json`
- `proofs/release_candidate/anomaly_reconciliation_result.json`

These files are the current repo-local reproducibility anchors for the
standalone `zpe-robotics` package surface. Historical bundles under
`proofs/artifacts/historical/` are lineage only.

## Golden-Bundle Hash

Will be populated by the `receipt-bundle.yml` workflow in Wave 3.

## Verification Command

```bash
pip install zpe-robotics
zpe-robotics --version
```

For repo-local verification:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[dev,benchmark,telemetry,netnew]"
python -m pytest tests -q
python -m build
```

## Supported Runtimes

- Python 3.11 and 3.12 are the declared CI runtime targets.
- Linux x86, macOS, and ARM64-QEMU parity evidence is recorded in
  `proofs/release_candidate/it04_parity_matrix_result.json`.
- The package remains a standalone Python package; no robotics `.zpbot` Rust ABI
  is wired into the runtime path today.
