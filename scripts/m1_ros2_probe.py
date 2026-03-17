#!/usr/bin/env python3
"""Standalone hosted/runtime probe for ROS 2 + MoveIt evidence."""

from __future__ import annotations

import argparse
import datetime as dt
import os
import platform
import json
import subprocess
import sys
import traceback
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

AUTHORITY_SURFACE = "zpbot-v2"
AUTHORITY_WIRE_COMPATIBILITY = "wire-v1"


@dataclass(frozen=True)
class CmdResult:
    command: str
    returncode: int
    stdout: str
    stderr: str


_MOVEIT_IMPORT_PROBES: tuple[tuple[str, str], ...] = (
    (
        "from moveit.planning import MoveItPy",
        "from moveit.planning import MoveItPy; print('moveit.planning:MoveItPy')",
    ),
    (
        "import moveit_py",
        "import moveit_py; print('moveit_py')",
    ),
    (
        "import moveit",
        "import moveit; print('moveit')",
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe ROS 2 and MoveIt runtime availability")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "proofs" / "reruns" / f"m1_ros2_probe_{dt.date.today().isoformat()}" / "m1_ros2_probe.json",
    )
    parser.add_argument(
        "--workflow-run-id",
        default=os.environ.get("GITHUB_RUN_ID", "local-dry-run"),
    )
    parser.add_argument(
        "--install-command",
        default="",
        help="Optional shell command run before probing MoveIt imports",
    )
    parser.add_argument(
        "--ros2-command",
        default="ros2",
        help="ROS 2 executable path or command name",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        return _run_probe(args)
    except Exception as exc:  # pragma: no cover - defensive artifact guarantee
        payload = _base_payload(args)
        payload.update(
            {
                "status": "FAIL",
                "ros2_version": "",
                "moveit_importable": False,
                "moveit_import_target": "",
                "pass_criteria": "real ros2 version string plus successful MoveIt Python import with exact failure preservation",
                "attempt_log": [],
                "unhandled_error": f"{type(exc).__name__}: {exc}",
                "traceback": traceback.format_exc(),
            }
        )
        _write_json(args.output, payload)
        return 1


def _run_probe(args: argparse.Namespace) -> int:
    payload = _base_payload(args)

    attempts: list[CmdResult] = []
    install_result: CmdResult | None = None
    if args.install_command:
        install_result = _run_shell(args.install_command)
        attempts.append(install_result)

    ros2_result = _run_cmd([args.ros2_command, "--version"])
    attempts.append(ros2_result)
    ros2_version = _extract_primary_output(ros2_result) if ros2_result.returncode == 0 else ""

    moveit_result, moveit_target = _probe_moveit_imports()
    attempts.extend(moveit_result)
    first_moveit_success = next((item for item in moveit_result if item.returncode == 0), None)

    payload.update(
        {
            "status": "PASS"
            if _is_pass(install_result, ros2_result, first_moveit_success)
            else "FAIL",
            "ros2_version": ros2_version,
            "moveit_importable": bool(first_moveit_success),
            "moveit_import_target": moveit_target,
            "pass_criteria": "real ros2 version string plus successful MoveIt Python import with exact failure preservation",
            "attempt_log": [asdict(item) for item in attempts],
        }
    )

    if not first_moveit_success:
        payload["moveit_error"] = _first_nonempty_error(moveit_result)
    if install_result is not None:
        payload["install_command_ran"] = True

    _write_json(args.output, payload)
    return 0 if payload["status"] == "PASS" else 1


def _base_payload(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "authority_surface": AUTHORITY_SURFACE,
        "compatibility_mode": AUTHORITY_WIRE_COMPATIBILITY,
        "generation_timestamp": _utc_now().isoformat(),
        "host_platform": platform.platform(),
        "platform": platform.platform(),
        "workflow_run_id": str(args.workflow_run_id),
    }


def _probe_moveit_imports() -> tuple[list[CmdResult], str]:
    results: list[CmdResult] = []
    for label, snippet in _MOVEIT_IMPORT_PROBES:
        result = _run_cmd([sys.executable, "-c", snippet], label=label)
        results.append(result)
        if result.returncode == 0:
            return results, label
    return results, ""


def _is_pass(
    install_result: CmdResult | None,
    ros2_result: CmdResult,
    moveit_success: CmdResult | None,
) -> bool:
    if install_result is not None and install_result.returncode != 0:
        return False
    if ros2_result.returncode != 0:
        return False
    if not _extract_primary_output(ros2_result):
        return False
    return moveit_success is not None


def _run_shell(command: str, timeout: int = 1800) -> CmdResult:
    return _run_cmd(["/bin/bash", "-lc", command], timeout=timeout)


def _run_cmd(command: list[str], timeout: int = 120, label: str | None = None) -> CmdResult:
    command_text = label or " ".join(command)
    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        return CmdResult(
            command=command_text,
            returncode=proc.returncode,
            stdout=(proc.stdout or "").strip(),
            stderr=(proc.stderr or "").strip(),
        )
    except FileNotFoundError as exc:
        return CmdResult(
            command=command_text,
            returncode=127,
            stdout="",
            stderr=f"{type(exc).__name__}: {exc}",
        )
    except subprocess.TimeoutExpired as exc:
        stdout = (exc.stdout or "").strip() if isinstance(exc.stdout, str) else ""
        stderr = (exc.stderr or "").strip() if isinstance(exc.stderr, str) else "timeout"
        return CmdResult(command=command_text, returncode=124, stdout=stdout, stderr=stderr)


def _extract_primary_output(result: CmdResult) -> str:
    text = result.stdout or result.stderr
    return text.splitlines()[0].strip() if text else ""


def _first_nonempty_error(results: list[CmdResult]) -> str:
    for result in results:
        if result.stderr:
            return result.stderr
        if result.stdout:
            return result.stdout
    return ""


def _utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
