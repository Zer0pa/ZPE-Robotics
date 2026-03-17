"""Reusable ROS2 plus MoveIt2 runtime probe helpers."""

from __future__ import annotations

import datetime as dt
import os
import platform
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .constants import ROS2_BRIDGE_PASS_CRITERIA
from .utils import write_json


ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class CmdResult:
    command: str
    returncode: int
    stdout: str
    stderr: str


def probe_ros2_moveit() -> dict[str, Any]:
    """Probe for a runnable ROS2 plus MoveIt2 path and bridge importability."""

    attempts: list[CmdResult] = []
    local_ros2 = _run_cmd(["ros2", "--version"], timeout=20)
    attempts.append(local_ros2)
    if local_ros2.returncode == 0:
        local_pkg = _run_cmd(["ros2", "pkg", "list"], timeout=40)
        attempts.append(local_pkg)
        if local_pkg.returncode == 0 and "moveit" in local_pkg.stdout.lower():
            return _probe_payload("PASS", "local", attempts)

    docker_bin = "/opt/homebrew/bin/docker" if Path("/opt/homebrew/bin/docker").exists() else "docker"
    docker_check = _run_cmd([docker_bin, "--version"], timeout=20)
    attempts.append(docker_check)
    if docker_check.returncode == 0:
        docker_ros2 = _run_cmd(
            [
                docker_bin,
                "run",
                "--rm",
                "docker.io/library/ros:humble-ros-base-jammy",
                "bash",
                "-lc",
                "ros2 --help >/dev/null && echo ROS2_OK",
            ],
            timeout=120,
        )
        attempts.append(docker_ros2)
        if docker_ros2.returncode != 0 and _docker_daemon_unavailable(docker_ros2):
            _ensure_docker_daemon(attempts)
            docker_ros2 = _run_cmd(
                [
                    docker_bin,
                    "run",
                    "--rm",
                    "docker.io/library/ros:humble-ros-base-jammy",
                    "bash",
                    "-lc",
                    "ros2 --help >/dev/null && echo ROS2_OK",
                ],
                timeout=120,
                env=_arm64_tools_env(),
            )
            attempts.append(docker_ros2)
        if docker_ros2.returncode == 0:
            docker_moveit = _run_cmd(
                [
                    docker_bin,
                    "run",
                    "--rm",
                    "docker.io/library/ros:humble-ros-base-jammy",
                    "bash",
                    "-lc",
                    (
                        "set -e; "
                        "apt-get update -qq >/dev/null; "
                        "DEBIAN_FRONTEND=noninteractive apt-get install -y -qq ros-humble-moveit >/dev/null; "
                        "ros2 pkg list | grep -i '^moveit' | head -n 1"
                    ),
                ],
                timeout=1200,
                env=_arm64_tools_env(),
            )
            attempts.append(docker_moveit)
            if docker_moveit.returncode == 0 and docker_moveit.stdout.strip():
                return _probe_payload("PASS", "docker", attempts)

    podman_bin = "/opt/homebrew/bin/podman" if Path("/opt/homebrew/bin/podman").exists() else "podman"
    podman_check = _run_cmd([podman_bin, "--version"], timeout=20)
    attempts.append(podman_check)
    if podman_check.returncode == 0:
        podman_start = _run_cmd([podman_bin, "machine", "start", "zpe-robotics-podman"], timeout=90)
        attempts.append(podman_start)
        if podman_start.returncode == 0:
            podman_moveit = _run_cmd(
                [
                    podman_bin,
                    "run",
                    "--rm",
                    "docker.io/library/ros:humble-ros-base-jammy",
                    "bash",
                    "-lc",
                    (
                        "set -e; "
                        "apt-get update -qq >/dev/null; "
                        "DEBIAN_FRONTEND=noninteractive apt-get install -y -qq ros-humble-moveit >/dev/null; "
                        "ros2 pkg list | grep -i '^moveit' | head -n 1"
                    ),
                ],
                timeout=1200,
            )
            attempts.append(podman_moveit)
            if podman_moveit.returncode == 0 and podman_moveit.stdout.strip():
                return _probe_payload("PASS", "podman", attempts)

    return _probe_payload("FAIL", "none", attempts)


def write_ros2_probe_artifact(output_path: Path) -> dict[str, Any]:
    """Run the probe and write the canonical artifact payload."""

    payload = probe_ros2_moveit()
    payload["generated_at"] = dt.datetime.now(dt.UTC).isoformat()
    payload["platform"] = platform.platform()
    write_json(output_path, payload)
    return payload


def _probe_payload(status: str, runtime_path: str, attempts: list[CmdResult]) -> dict[str, Any]:
    return {
        "status": status if _bridge_import_ok() else "FAIL",
        "runtime_path": runtime_path,
        "bridge_module": _bridge_module_status(),
        "attempts": [asdict(item) for item in attempts],
        "pass_criteria": ROS2_BRIDGE_PASS_CRITERIA,
    }


def _bridge_import_ok() -> bool:
    return bool(_bridge_module_status()["importable"])


def _bridge_module_status() -> dict[str, Any]:
    try:
        __import__("zpe_robotics.mcap_bridge")
    except Exception as exc:  # pragma: no cover - exercised in runtime probe execution
        return {"module": "zpe_robotics.mcap_bridge", "importable": False, "error": f"{type(exc).__name__}: {exc}"}
    return {"module": "zpe_robotics.mcap_bridge", "importable": True, "error": ""}


def _run_cmd(command: list[str], timeout: int = 120, env: dict[str, str] | None = None) -> CmdResult:
    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=timeout, env=env)
        return CmdResult(
            command=" ".join(command),
            returncode=proc.returncode,
            stdout=(proc.stdout or "").strip(),
            stderr=(proc.stderr or "").strip(),
        )
    except FileNotFoundError as exc:
        return CmdResult(command=" ".join(command), returncode=127, stdout="", stderr=f"{type(exc).__name__}: {exc}")
    except subprocess.TimeoutExpired as exc:
        stdout = (exc.stdout or "").strip() if isinstance(exc.stdout, str) else ""
        stderr = (exc.stderr or "").strip() if isinstance(exc.stderr, str) else "timeout"
        return CmdResult(command=" ".join(command), returncode=124, stdout=stdout, stderr=stderr)


def _arm64_tools_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PATH"] = "/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
    return env


def _docker_daemon_unavailable(result: CmdResult) -> bool:
    text = f"{result.stdout}\n{result.stderr}".lower()
    return "cannot connect to the docker daemon" in text


def _ensure_docker_daemon(attempts: list[CmdResult]) -> None:
    colima_bin = "/opt/homebrew/bin/colima" if Path("/opt/homebrew/bin/colima").exists() else "colima"
    env = _arm64_tools_env()
    status = _run_cmd([colima_bin, "status"], timeout=40, env=env)
    attempts.append(status)
    if status.returncode == 0 and "running" in status.stdout.lower():
        return
    start = _run_cmd([colima_bin, "start", "--cpu", "4", "--memory", "8", "--disk", "60"], timeout=1200, env=env)
    attempts.append(start)
