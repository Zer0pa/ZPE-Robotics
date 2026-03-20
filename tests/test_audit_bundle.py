from __future__ import annotations

import json
from pathlib import Path

from zpe_robotics.audit_bundle import build_provenance_manifest, evaluate_corruption_matrix, generate_audit_bundle
from zpe_robotics.release_candidate import build_single_packet_composition
from zpe_robotics.utils import sha256_file


def test_build_provenance_manifest_matches_packet_surface(tmp_path: Path) -> None:
    composition = build_single_packet_composition()
    packet_path = tmp_path / "canonical.zpbot"
    packet_path.write_bytes(composition.packet)

    manifest = build_provenance_manifest(packet_path)

    assert manifest["status"] == "PASS"
    assert manifest["authority_surface"] == "zpbot-v2"
    assert manifest["compatibility_mode"] == "wire-v1"
    assert manifest["packet_sha256"] == sha256_file(packet_path)
    assert manifest["decoded_shape"] == list(composition.trajectory.shape)
    assert manifest["reference_roundtrip_sha256"] == manifest["replay_sha256"]
    assert manifest["source_paths"]


def test_corruption_matrix_records_expected_failures(tmp_path: Path) -> None:
    composition = build_single_packet_composition()
    packet_path = tmp_path / "canonical.zpbot"
    packet_path.write_bytes(composition.packet)

    matrix = evaluate_corruption_matrix(packet_path)

    assert matrix["status"] == "PASS"
    observed = {case["case_id"]: case for case in matrix["cases"]}
    assert observed["invalid_magic"]["actual_failure"] == "invalid packet magic"
    assert observed["crc_mismatch"]["actual_failure"] == "payload CRC mismatch"
    assert observed["truncated_header"]["actual_failure"] == "blob too small for packet header"
    assert observed["unsupported_version"]["actual_failure"] == "unsupported codec version 99"


def test_generate_audit_bundle_writes_expected_files(tmp_path: Path) -> None:
    composition = build_single_packet_composition()
    packet_path = tmp_path / "canonical.zpbot"
    packet_path.write_bytes(composition.packet)

    summary = generate_audit_bundle(packet_path, tmp_path / "comm03")

    assert summary["status"] == "PASS"
    manifest_path = Path(summary["manifest_path"])
    corruption_path = Path(summary["corruption_matrix_path"])
    assert manifest_path.exists()
    assert corruption_path.exists()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    corruption = json.loads(corruption_path.read_text(encoding="utf-8"))
    assert manifest["packet_sha256"] == summary["packet_sha256"]
    assert corruption["status"] == "PASS"
