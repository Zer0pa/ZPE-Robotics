# Gate M1 Runbook: GitHub Actions Hosted Probe

## Objective

Execute the first hosted Ubuntu `M1` probe surface and preserve a decisive JSON artifact whether the result is `PASS` or `FAIL`.

## Local Dry Run

1. `M1_LOCAL_ROOT="proofs/reruns/m1_ros2_probe_local"`
2. `python -m py_compile scripts/m1_ros2_probe.py`
3. `python scripts/m1_ros2_probe.py --workflow-run-id local-dry-run --output "$M1_LOCAL_ROOT/m1_ros2_probe_local.json"`

## Hosted Run

1. Push the workflow-bearing branch to GitHub.
2. Dispatch `.github/workflows/m1_ros2_probe.yml` with `workflow_dispatch`.
3. Download artifact `m1-ros2-probe-evidence`.

## Expected Output

- `proofs/reruns/m1_ros2_probe_<run-id>/m1_ros2_probe_result.json`

## Pass Condition

`M1` can be treated as closed only when the hosted artifact reports all of:

- `status = PASS`
- `ros2_pkg_list_ok = true`
- a recorded non-empty `ros2_version` provenance field
- `moveit_importable = true`
- required provenance fields:
  - `authority_surface = zpbot-v2`
  - `compatibility_mode = wire-v1`
  - `generation_timestamp`
  - `host_platform`
  - `workflow_run_id`

## Fail Signatures

- artifact missing
- `status = FAIL`
- `ros2 pkg list` exits non-zero
- empty or missing `ros2_version`
- `moveit_importable = false`
- missing provenance fields

## Scope Guard

- Local dry runs stage the probe path only. They do not close `M1`.
- The workflow must fail loudly on a failing artifact; uploading evidence alone is not success.
