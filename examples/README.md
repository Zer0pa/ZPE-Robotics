# Examples

Runnable example surfaces for the current `zpe-robotics` package.

## Quick Fixture Runs

```bash
python examples/lerobot_compress.py --output-dir ./example_output/lerobot
python examples/rosbag_bridge.py --output-dir ./example_output/rosbag
python examples/mcap_bridge.py --output-dir ./example_output/mcap
```

## Bounded LeRobot Download

```bash
python -m pip install -e ".[dev,benchmark]"
python scripts/acquire_enterprise_dataset.py --repo-id lerobot/columbia_cairlab_pusht_real --data-root ./example_data --output ./example_data/pusht_real_provenance.json --include-namespace --require-real
python examples/lerobot_compress.py --dataset-root ./example_data/lerobot__columbia_cairlab_pusht_real --repo-id lerobot/columbia_cairlab_pusht_real --output-dir ./example_output/lerobot_real
```

## Notes

- `lerobot_compress.py` defaults to a local fixture so it runs in CI and clean clones without benchmark extras.
- `rosbag_bridge.py` exercises deterministic bag -> `.zpbot` -> deterministic bag roundtrip.
- `mcap_bridge.py` exercises native MCAP-backed records plus metadata search without trajectory decode.
