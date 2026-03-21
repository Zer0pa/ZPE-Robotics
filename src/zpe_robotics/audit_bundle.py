"""COMM-03 audit bundle helpers over the frozen zpbot-v2 surface."""

from __future__ import annotations

import datetime as dt
import platform
from pathlib import Path
from typing import Any, Callable

from .release_candidate import compute_reference_bridge_roundtrip
from .utils import ensure_dir, sha256_file, write_json
from .wire import HEADER_SIZE, WireFormatError, decode_packet, describe_packet


Mutation = Callable[[bytes], bytes]


def build_provenance_manifest(packet_path: str | Path, *, source_paths: list[str] | None = None) -> dict[str, Any]:
    """Build the COMM-03 manifest for a canonical packet artifact."""

    path = Path(packet_path)
    blob = path.read_bytes()
    packet_info = describe_packet(blob)
    trajectory = decode_packet(blob)
    replay_report = compute_reference_bridge_roundtrip()

    return {
        "status": "PASS" if replay_report["bit_consistent"] else "FAIL",
        "authority_surface": str(packet_info["authority_surface"]),
        "compatibility_mode": str(packet_info["compatibility_mode"]),
        "generation_timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
        "host_platform": platform.platform(),
        "packet_path": str(path),
        "packet_sha256": sha256_file(path),
        "packet_info": packet_info,
        "decoded_shape": list(trajectory.shape),
        "replay_sha256": str(replay_report["replay_sha256"]),
        "reference_roundtrip_sha256": str(replay_report["original_sha256"]),
        "source_paths": source_paths or _default_source_paths(path),
    }


def evaluate_corruption_matrix(packet_path: str | Path) -> dict[str, Any]:
    """Evaluate the canonical malformed-input cases for COMM-03."""

    path = Path(packet_path)
    blob = path.read_bytes()
    cases: list[dict[str, Any]] = []

    for case_id, mutation, expected_failure, mutator in _corruption_cases():
        corrupted = mutator(blob)
        actual_failure = ""
        status = "FAIL"
        try:
            decode_packet(corrupted)
            actual_failure = "NO_ERROR"
        except WireFormatError as exc:
            actual_failure = str(exc)
            status = "PASS" if actual_failure == expected_failure else "FAIL"

        cases.append(
            {
                "case_id": case_id,
                "mutation": mutation,
                "expected_failure": expected_failure,
                "actual_failure": actual_failure,
                "status": status,
            }
        )

    return {
        "status": "PASS" if all(case["status"] == "PASS" for case in cases) else "FAIL",
        "generation_timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
        "packet_path": str(path),
        "packet_sha256": sha256_file(path),
        "cases": cases,
    }


def generate_audit_bundle(
    packet_path: str | Path,
    output_dir: str | Path,
    *,
    source_paths: list[str] | None = None,
) -> dict[str, Any]:
    """Generate the manifest and corruption artifacts for COMM-03."""

    out_dir = Path(output_dir)
    ensure_dir(out_dir)

    manifest_path = out_dir / "comm03_provenance_manifest.json"
    corruption_path = out_dir / "comm03_corruption_matrix.json"

    manifest = build_provenance_manifest(packet_path, source_paths=source_paths)
    corruption = evaluate_corruption_matrix(packet_path)

    write_json(manifest_path, manifest)
    write_json(corruption_path, corruption)

    status = "PASS" if manifest["status"] == "PASS" and corruption["status"] == "PASS" else "FAIL"
    return {
        "status": status,
        "manifest_path": str(manifest_path),
        "corruption_matrix_path": str(corruption_path),
        "packet_sha256": str(manifest["packet_sha256"]),
        "replay_sha256": str(manifest["replay_sha256"]),
        "corruption_cases": len(corruption["cases"]),
    }


def _default_source_paths(packet_path: Path) -> list[str]:
    return [
        str(packet_path),
        "zpe-robotics/docs/ZPBOT_V2_AUTHORITY_SURFACE.md",
        "zpe-robotics/RELEASE_CANDIDATE.md",
        "zpe-robotics/proofs/red_team/red_team_report.json",
    ]


def _corruption_cases() -> tuple[tuple[str, str, str, Mutation], ...]:
    return (
        ("invalid_magic", "replace packet magic with BAD!!", "invalid packet magic", _mutate_invalid_magic),
        ("crc_mismatch", "flip the last payload byte", "payload CRC mismatch", _mutate_crc_mismatch),
        ("truncated_header", "truncate below header size", "blob too small for packet header", _mutate_truncated_header),
        ("unsupported_version", "set wire version byte to 99", "unsupported codec version 99", _mutate_unsupported_version),
    )


def _mutate_invalid_magic(blob: bytes) -> bytes:
    return b"BAD!!" + blob[5:]


def _mutate_crc_mismatch(blob: bytes) -> bytes:
    tampered = bytearray(blob)
    tampered[-1] ^= 0x7F
    return bytes(tampered)


def _mutate_truncated_header(blob: bytes) -> bytes:
    return blob[: HEADER_SIZE - 1]


def _mutate_unsupported_version(blob: bytes) -> bytes:
    tampered = bytearray(blob)
    tampered[5] = 99
    return bytes(tampered)
