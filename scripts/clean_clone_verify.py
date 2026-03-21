#!/usr/bin/env python3
"""Hosted clean-clone verification helper for the release candidate."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


AUTHORITY_SURFACE = "zpbot-v2"
COMPATIBILITY_MODE = "wire-v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify clean-clone installability and CLI behavior.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workflow-run-id", default="local-dry-run")
    return parser.parse_args()


def run_command(cmd: list[str], cwd: Path) -> dict[str, object]:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "command": cmd,
        "cwd": str(cwd),
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def summarize_failure(step: str, result: dict[str, object]) -> str:
    stdout = str(result.get("stdout", "")).strip()
    stderr = str(result.get("stderr", "")).strip()
    detail = stderr or stdout or f"returncode={result.get('returncode')}"
    return f"{step}: {detail}"


def build_fixture_bag(python_bin: Path, repo_root: Path, bag_path: Path) -> dict[str, object]:
    code = """
from pathlib import Path
import sys
from zpe_robotics.release_candidate import build_canonical_arm_fixture, encode_single_record_bag

bag_path = Path(sys.argv[1])
trajectory = build_canonical_arm_fixture()
bag_path.write_bytes(encode_single_record_bag(trajectory))
print(str(bag_path))
""".strip()
    return run_command([str(python_bin), "-c", code, str(bag_path)], cwd=repo_root)


def inspect_replay_bag(python_bin: Path, repo_root: Path, replay_path: Path) -> dict[str, object]:
    code = """
from pathlib import Path
import json
import sys
from zpe_robotics.release_candidate import default_codec
from zpe_robotics.rosbag_adapter import decode_records

replay_path = Path(sys.argv[1])
records = decode_records(replay_path.read_bytes(), default_codec(), decode_trajectory=True, strict_index=True)
payload = {
    "records": len(records),
    "trajectory_shape": list(records[0]["trajectory"].shape) if records else [],
}
print(json.dumps(payload, sort_keys=True))
""".strip()
    return run_command([str(python_bin), "-c", code, str(replay_path)], cwd=repo_root)


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    output_path = args.output.resolve() if args.output.is_absolute() else (repo_root / args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    timestamp = dt.datetime.now(dt.timezone.utc).isoformat()
    host_platform = platform.platform()
    attempt_log: list[dict[str, object]] = []
    install_ok = False
    cli_ok = False
    tests_ok = False
    failure = ""
    cli_details: dict[str, object] = {}

    venv_parent = Path(tempfile.mkdtemp(prefix="zpe_clean_clone_venv_"))
    work_dir = Path(tempfile.mkdtemp(prefix="zpe_clean_clone_work_"))
    venv_dir = venv_parent / "venv"
    python_bin = venv_dir / "bin" / "python"
    pip_cmd = [str(python_bin), "-m", "pip"]
    pytest_cmd = [str(python_bin), "-m", "pytest", "tests", "-q"]
    zpe_bin = venv_dir / "bin" / "zpe"

    try:
        result = run_command([sys.executable, "-m", "venv", str(venv_dir)], cwd=repo_root)
        attempt_log.append({"step": "create_venv", **result})
        if result["returncode"] != 0:
            failure = summarize_failure("create_venv", result)
            raise RuntimeError(failure)

        result = run_command(pip_cmd + ["install", "-e", "."], cwd=repo_root)
        attempt_log.append({"step": "pip_install_editable", **result})
        install_ok = result["returncode"] == 0
        if not install_ok:
            failure = summarize_failure("pip_install_editable", result)
            raise RuntimeError(failure)

        result = run_command(pip_cmd + ["install", "pytest"], cwd=repo_root)
        attempt_log.append({"step": "pip_install_pytest", **result})
        if result["returncode"] != 0:
            failure = summarize_failure("pip_install_pytest", result)
            raise RuntimeError(failure)

        result = run_command([str(zpe_bin), "--version"], cwd=repo_root)
        attempt_log.append({"step": "zpe_version", **result})
        if result["returncode"] != 0:
            failure = summarize_failure("zpe_version", result)
            raise RuntimeError(failure)
        cli_details["version"] = str(result["stdout"]).strip()

        bag_path = work_dir / "arm_fixture.bag"
        packet_path = work_dir / "arm_fixture.zpbot"
        replay_path = work_dir / "arm_fixture_replay.bag"

        result = build_fixture_bag(python_bin, repo_root, bag_path)
        attempt_log.append({"step": "build_fixture_bag", **result})
        if result["returncode"] != 0:
            failure = summarize_failure("build_fixture_bag", result)
            raise RuntimeError(failure)

        result = run_command([str(zpe_bin), "encode", str(bag_path), str(packet_path)], cwd=repo_root)
        attempt_log.append({"step": "zpe_encode", **result})
        if result["returncode"] != 0:
            failure = summarize_failure("zpe_encode", result)
            raise RuntimeError(failure)

        result = run_command([str(zpe_bin), "verify", str(packet_path)], cwd=repo_root)
        attempt_log.append({"step": "zpe_verify", **result})
        if result["returncode"] != 0:
            failure = summarize_failure("zpe_verify", result)
            raise RuntimeError(failure)
        cli_details["verify_payload"] = json.loads(str(result["stdout"]))

        result = run_command([str(zpe_bin), "decode", str(packet_path), str(replay_path)], cwd=repo_root)
        attempt_log.append({"step": "zpe_decode", **result})
        if result["returncode"] != 0:
            failure = summarize_failure("zpe_decode", result)
            raise RuntimeError(failure)

        result = inspect_replay_bag(python_bin, repo_root, replay_path)
        attempt_log.append({"step": "inspect_replay_bag", **result})
        if result["returncode"] != 0:
            failure = summarize_failure("inspect_replay_bag", result)
            raise RuntimeError(failure)
        cli_details["replay_payload"] = json.loads(str(result["stdout"]))
        cli_details["artifacts"] = {
            "bag_path": str(bag_path),
            "packet_path": str(packet_path),
            "replay_path": str(replay_path),
        }
        cli_ok = True

        result = run_command(pytest_cmd, cwd=repo_root)
        attempt_log.append({"step": "pytest_tests", **result})
        tests_ok = result["returncode"] == 0
        if not tests_ok:
            failure = summarize_failure("pytest_tests", result)
            raise RuntimeError(failure)
    except Exception as exc:  # noqa: BLE001
        if not failure:
            failure = str(exc)
    finally:
        payload = {
            "authority_surface": AUTHORITY_SURFACE,
            "compatibility_mode": COMPATIBILITY_MODE,
            "generation_timestamp": timestamp,
            "timestamp": timestamp,
            "host_platform": host_platform,
            "platform": host_platform,
            "workflow_run_id": args.workflow_run_id,
            "status": "PASS" if install_ok and cli_ok and tests_ok else "FAIL",
            "install_ok": install_ok,
            "cli_ok": cli_ok,
            "tests_ok": tests_ok,
            "failure": failure,
            "repo_root": str(repo_root),
            "python_bin": str(python_bin),
            "zpe_bin": str(zpe_bin),
            "cli_details": cli_details,
            "attempt_log": attempt_log,
        }
        output_path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
        shutil.rmtree(venv_parent, ignore_errors=True)
        shutil.rmtree(work_dir, ignore_errors=True)

    return 0 if install_ok and cli_ok and tests_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
