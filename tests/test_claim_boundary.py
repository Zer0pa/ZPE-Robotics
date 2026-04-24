from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def _read_json(relative_path: str) -> dict[str, object]:
    return json.loads(_read_text(relative_path))


def test_narrow_claim_gate_ratifies_only_reduced_surface() -> None:
    gate = _read_json("proofs/narrow_claim/NARROW_CLAIM_GATE.json")

    assert gate["status"] == "PASS"
    assert gate["selected_gate"] == "narrow_claim"
    assert gate["commercial_readiness"] == "BLOCKED_FOR_FULL_RELEASE"
    assert "bounded_lossy_robot_motion_telemetry_archive" in gate["ratified_surface"]
    assert "decoded_primitive_index_search" in gate["ratified_surface"]

    non_claims = set(gate["explicit_non_claims"])
    assert "lossless_codec" in non_claims
    assert "bit_exact_replay" in non_claims
    assert "search_without_decode" in non_claims
    assert "live_robot_control_loop" in non_claims
    assert "imc_integrated_robotics_rust_abi" in non_claims
    assert "full_release_readiness" in non_claims


def test_narrow_claim_gate_preserves_sovereign_blockers() -> None:
    gate = _read_json("proofs/narrow_claim/NARROW_CLAIM_GATE.json")
    blockers = {str(item["id"]): item for item in gate["unresolved_blockers"]}

    assert blockers["B3"]["status"] == "FAIL"
    assert blockers["red_team_attack_3"]["status"] == "FAIL"
    assert blockers["red_team_attack_4"]["status"] == "PARTIAL"
    assert blockers["red_team_attack_7"]["status"] == "OPEN"
    assert blockers["robotics_rust_abi"]["status"] == "MISSING"


def test_narrow_claim_authority_paths_exist() -> None:
    gate = _read_json("proofs/narrow_claim/NARROW_CLAIM_GATE.json")
    for relative_path in gate["authority_files"]:
        assert (ROOT / str(relative_path)).exists(), relative_path

    registry = _read_text("docs/DOC_REGISTRY.md")
    assert "docs/CLAIM_BOUNDARY.md" in registry
    assert "docs/MECHANICS_LAYER.md" in registry
    assert "proofs/narrow_claim/NARROW_CLAIM_GATE.json" in registry


def test_frontdoor_routes_to_narrow_claim_without_release_overclaim() -> None:
    readme = _read_text("README.md")
    claim_boundary = _read_text("docs/CLAIM_BOUNDARY.md")
    mechanics = _read_text("docs/MECHANICS_LAYER.md")

    assert "proofs/narrow_claim/NARROW_CLAIM_GATE.json" in readme
    assert "| Verdict | BLOCKED |" in readme
    assert "bounded-lossy archive/search" in readme
    assert "search without decode" in claim_boundary
    assert "live robot control" in claim_boundary
    assert "full engineering remains blocked" in mechanics
