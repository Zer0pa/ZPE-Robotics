# Max Resource Validation Log

## AgiBot World
- primary_command: `load_dataset('agibot-world/AgiBotWorld-Beta', split='train', streaming=True)`
- primary_result: FAIL (DatasetNotFoundError: Dataset 'agibot-world/AgiBotWorld-Beta' is a gated dataset on the Hub. Visit the dataset page at https://huggingface.co/datasets/agibot-world/AgiBotWorld-Beta to ask for access.)
- fallback_command: `load_dataset('parquet', data_files={'train':['hf://datasets/weijian-sun/agibotworld-lerobot/task_327/data/chunk-000/episode_000000.parquet']}, split='train', streaming=True)`
- fallback_result: PASS (samples=128)

## Open X-Embodiment
- primary_command: `load_dataset('jxu124/OpenX-Embodiment', split='train', streaming=True)`
- primary_result: FAIL (RuntimeError: Dataset scripts are no longer supported, but found OpenX-Embodiment.py)
- fallback_command: `load_dataset('IVC-liuyuan/Swift-OpenX-Embodiment-action-chunk-jsons', split='train', streaming=True)`
- fallback_result: PASS (samples=128)

## RH20T
- command: `load_dataset('hainh22/rh20t', split='train', streaming=True)`
- result: PASS (samples=128)

## LeRobot Direct Run
- command: `load_dataset('lerobot/svla_so101_pickplace', split='train', streaming=True)`
- result: PASS (samples=128)

## LIBERO Direct Run
- command: `load_dataset('whosricky/libero_spatial_v30', split='train', streaming=True)`
- result: PASS (samples=128)

## ROS2 / MoveIt2 Runtime
- attempt_1_command: `ros2 --version`
- attempt_1_returncode: 127
- attempt_1_error: FileNotFoundError: [Errno 2] No such file or directory: 'ros2'
- attempt_2_command: `/opt/homebrew/bin/docker --version`
- attempt_2_returncode: 0
- attempt_3_command: `/opt/homebrew/bin/docker run --rm docker.io/library/ros:humble-ros-base-jammy bash -lc ros2 --help >/dev/null && echo ROS2_OK`
- attempt_3_returncode: 0
- attempt_4_command: `/opt/homebrew/bin/docker run --rm docker.io/moveit/moveit2:humble-source bash -lc ros2 pkg list | grep -i '^moveit' | head -n 1`
- attempt_4_returncode: 125
- attempt_4_error: Unable to find image 'moveit/moveit2:humble-source' locally
docker: Error response from daemon: no matching manifest for linux/arm64/v8 in the manifest list entries: no match for platform in manifest: not found

Run 'docker run --help' for 
- attempt_5_command: `/opt/homebrew/bin/docker run --rm docker.io/library/ros:humble-ros-base-jammy bash -lc set -e; apt-get update -qq >/dev/null; DEBIAN_FRONTEND=noninteractive apt-get install -y -qq ros-humble-moveit >/dev/null; ros2 pkg list | grep -i '^moveit' | head -n 1`
- attempt_5_returncode: 0
- runtime_path: docker
- result: PASS

## MuJoCo Runtime
- attempt_1_command: `/Users/zer0pa-build/ZPE Multimodality/ZPE Robotics/.venv/bin/python -c import mujoco; print('MUJOCO_OK', mujoco.__version__)`
- attempt_1_returncode: 1
- attempt_1_error: Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import mujoco; print('MUJOCO_OK', mujoco.__version__)
    ^^^^^^^^^^^^^
ModuleNotFoundError: No module named 'mujoco'
- attempt_2_command: `/opt/homebrew/bin/python3.11 -c import platform,sys; print(platform.machine()); print(sys.version.split()[0])`
- attempt_2_returncode: 0
- attempt_3_command: `/opt/homebrew/bin/python3.11 -m venv /Users/zer0pa-build/ZPE Multimodality/ZPE Robotics/.venv_mujoco_arm64`
- attempt_3_returncode: 0
- attempt_4_command: `/Users/zer0pa-build/ZPE Multimodality/ZPE Robotics/.venv_mujoco_arm64/bin/python -m pip install -q --upgrade pip setuptools wheel`
- attempt_4_returncode: 0
- attempt_5_command: `/Users/zer0pa-build/ZPE Multimodality/ZPE Robotics/.venv_mujoco_arm64/bin/python -m pip install -q mujoco==3.5.0 --only-binary=:all:`
- attempt_5_returncode: 0
- attempt_6_command: `/Users/zer0pa-build/ZPE Multimodality/ZPE Robotics/.venv_mujoco_arm64/bin/python /Users/zer0pa-build/ZPE Multimodality/ZPE Robotics/scripts/mujoco_parity_probe.py --output artifacts/2026-02-20_zpe_robotics_wave1/mujoco_parity_report.json --seed 20260220 --samples 128`
- attempt_6_returncode: 0
- selected_python: /Users/zer0pa-build/ZPE Multimodality/ZPE Robotics/.venv_mujoco_arm64/bin/python
- result: PASS

## Octo Policy Comparator
- attempt_1_command: `HF_HOME=/Users/zer0pa-build/ZPE Multimodality/ZPE Robotics/.hf_cache_octo /Users/zer0pa-build/ZPE Multimodality/ZPE Robotics/.venv/bin/python -c from octo.model.octo_model import OctoModel; OctoModel.load_pretrained('hf://rail-berkeley/octo-base'); print('OCTO_OK') # model=rail-berkeley/octo-base`
- attempt_1_returncode: 1
- attempt_1_error: Traceback (most recent call last):
  File "<string>", line 1, in <module>
    from octo.model.octo_model import OctoModel; OctoModel.load_pretrained('hf://rail-berkeley/octo-base'); print('OCTO_OK')
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
- attempt_2_command: `HF_HOME=/Users/zer0pa-build/ZPE Multimodality/ZPE Robotics/.hf_cache_octo /Users/zer0pa-build/ZPE Multimodality/ZPE Robotics/.venv_octo_arm64/bin/python -c from octo.model.octo_model import OctoModel; OctoModel.load_pretrained('hf://rail-berkeley/octo-small'); print('OCTO_OK') # model=rail-berkeley/octo-small`
- attempt_2_returncode: 0
- selected_python: /Users/zer0pa-build/ZPE Multimodality/ZPE Robotics/.venv_octo_arm64/bin/python
- result: PASS
