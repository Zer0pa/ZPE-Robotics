# Reproducibility

## Canonical Inputs

- `proofs/enterprise_benchmark/dataset_provenance.json` — governing real-dataset benchmark provenance.
- `proofs/artifacts/lerobot_expanded_benchmarks/dataset_manifest.json` — qualified LeRobot dataset ledger for the expanded benchmark sweep.
- `proofs/release_candidate/canonical_release_packet.zpbot` — canonical packet used by the release-candidate replay surface.
- `proofs/release_candidate/anomaly_threshold_sweep.json` — declared anomaly-threshold sweep that selected the current attack-5 threshold surface.

## Golden-Bundle Hash

This will be populated by the `receipt-bundle.yml` workflow in Wave 3.

## Verification Command

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[dev,benchmark,telemetry,netnew]"
python -m pytest tests -q
python -m build
```

## Supported Runtimes

- Python `3.11` and `3.12`
- Standalone package verification on the committed parity surfaces in `proofs/release_candidate/it04_parity_matrix_result.json`
- Python 3.12 replay parity evidence in `proofs/red_team/python312_parity.log`
