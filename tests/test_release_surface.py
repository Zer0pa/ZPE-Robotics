from __future__ import annotations

import json
from pathlib import Path
import re
import tomllib


ROOT = Path(__file__).resolve().parents[1]


def _load_pyproject() -> dict[str, object]:
    with (ROOT / "pyproject.toml").open("rb") as handle:
        return tomllib.load(handle)


def _read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_sidecar_dependencies_are_optional() -> None:
    payload = _load_pyproject()
    project = payload["project"]
    dependencies = project["dependencies"]
    extras = project["optional-dependencies"]

    assert "benchmark" in extras
    assert "telemetry" in extras

    for prefix in ("comet-ml", "opik", "pyarrow", "h5py", "lz4", "zstandard"):
        assert not any(item.startswith(prefix) for item in dependencies)

    for prefix in ("datasets", "huggingface-hub", "pyarrow", "h5py", "lz4", "zstandard"):
        assert any(item.startswith(prefix) for item in extras["benchmark"])

    for prefix in ("comet-ml", "opik"):
        assert any(item.startswith(prefix) for item in extras["telemetry"])


def test_uv_sync_paths_match_declared_dev_extra() -> None:
    workflow_targets = [
        ROOT / ".github/workflows/e_g3_comparator.yml",
        ROOT / ".github/workflows/it03_it05_composition.yml",
        ROOT / ".github/workflows/it04_parity_matrix.yml",
        ROOT / ".github/workflows/m1_ros2_probe.yml",
    ]
    for path in workflow_targets:
        text = path.read_text(encoding="utf-8")
        assert "uv sync --dev" not in text
        assert "uv sync --frozen --extra dev" in text

    script_text = (ROOT / "scripts/arm64_parity_probe.py").read_text(encoding="utf-8")
    assert '"--dev"' not in script_text
    assert '"sync", "--frozen", "--extra", "dev"' in script_text


def test_publish_workflow_uses_oidc_pypi_surface() -> None:
    text = (ROOT / ".github/workflows/publish.yml").read_text(encoding="utf-8")
    assert "name: pypi" in text
    assert "id-token: write" in text
    assert "skip-existing: true" in text
    assert "gh-action-pypi-publish@release/v1" in text


def test_test_workflow_covers_python312() -> None:
    text = (ROOT / ".github/workflows/test.yml").read_text(encoding="utf-8")
    assert 'python-version: ["3.11", "3.12"]' in text


def test_clean_clone_verify_checks_cli_version() -> None:
    text = (ROOT / "scripts/clean_clone_verify.py").read_text(encoding="utf-8")
    assert '[str(zpe_bin), "--version"]' in text


def test_license_uses_five_year_change_date() -> None:
    text = _read_text("LICENSE")
    assert "five (5) years after the date of first public release" in text


def test_root_readme_keeps_expected_gif_surface() -> None:
    text = _read_text("README.md")
    gif_refs = re.findall(r'\.github/assets/readme/[^"]+\.gif', text)
    assert gif_refs == [
        ".github/assets/readme/zpe-masthead.gif",
        ".github/assets/readme/zpe-masthead-option-3-2.gif",
        ".github/assets/readme/zpe-masthead-option-3-3.gif",
    ]


def test_docs_surface_uses_shared_masthead_only() -> None:
    doc_paths = [
        "CHANGELOG.md",
        "CODE_OF_CONDUCT.md",
        "CONTRIBUTING.md",
        "GOVERNANCE.md",
        "RELEASING.md",
        "SECURITY.md",
        "docs/README.md",
        "docs/ARCHITECTURE.md",
        "docs/AUDITOR_PLAYBOOK.md",
        "docs/DOC_REGISTRY.md",
        "docs/FAQ.md",
        "docs/LEGAL_BOUNDARIES.md",
        "docs/OPERATOR_RUNBOOK.md",
        "docs/PUBLIC_AUDIT_LIMITS.md",
        "docs/RELEASE_CANDIDATE.md",
        "docs/SUPPORT.md",
        "docs/ZPBOT_V2_AUTHORITY_SURFACE.md",
        "docs/family/ROBOTICS_RELEASE_LINKAGE.md",
    ]

    for relative_path in doc_paths:
        text = _read_text(relative_path)
        if relative_path.startswith("docs/family/"):
            expected = "../../.github/assets/readme/zpe-masthead.gif"
        elif relative_path.startswith("docs/"):
            expected = "../.github/assets/readme/zpe-masthead.gif"
        else:
            expected = ".github/assets/readme/zpe-masthead.gif"

        gif_lines = [line.strip() for line in text.splitlines() if ".gif" in line]
        assert len(gif_lines) == 1, relative_path
        assert expected in gif_lines[0], relative_path
        assert expected in "\n".join(text.splitlines()[:5]), relative_path


def test_frontdoor_docs_do_not_describe_repo_as_private_staging() -> None:
    doc_paths = [
        "README.md",
        "docs/AUDITOR_PLAYBOOK.md",
        "docs/LEGAL_BOUNDARIES.md",
        "docs/PUBLIC_AUDIT_LIMITS.md",
    ]
    banned_phrases = [
        "private repository",
        "private staging only",
        "private github repo",
    ]

    for relative_path in doc_paths:
        text = _read_text(relative_path).lower()
        for phrase in banned_phrases:
            assert phrase not in text, f"{relative_path} contains {phrase!r}"


def test_pyproject_exposes_augmented_project_metadata() -> None:
    payload = _load_pyproject()
    project = payload["project"]

    assert project["authors"] == [{"name": "Zer0pa"}]
    assert project["urls"] == {
        "Homepage": "https://github.com/Zer0pa/ZPE-Robotics",
        "Documentation": "https://github.com/Zer0pa/ZPE-Robotics/tree/main/docs",
        "Repository": "https://github.com/Zer0pa/ZPE-Robotics",
        "Changelog": "https://github.com/Zer0pa/ZPE-Robotics/blob/main/CHANGELOG.md",
    }

    classifiers = set(project["classifiers"])
    assert "Framework :: Robot Framework" in classifiers
    assert "Topic :: Scientific/Engineering" in classifiers
    assert "Programming Language :: Python :: 3.11" in classifiers
    assert "Programming Language :: Python :: 3.12" in classifiers


def test_root_readme_has_phase1_augmentation_surface() -> None:
    text = _read_text("README.md")

    assert "Works with: `ROS2 Humble` | `MCAP` | `LeRobot` | `HuggingFace`" in text
    assert "Personas: imitation learning researcher. Fleet telemetry engineer." in text
    assert "| `zpe-robotics` | `186.05x` |" in text
    assert "| `gzip -9` | `10.97x` |" in text
    assert "| `lz4` | `8.31x` |" in text
    assert "Use ZPE-Robotics when motion traces must stay compact, deterministic, and searchable after capture." in text
    assert "[Foxglove Studio docs](https://docs.foxglove.dev/)" in text
    assert 'python -m pip install -e ".[dev]"' in text
    assert "zpe-robotics --version" in text


def test_root_readme_baseline_snapshot_matches_benchmark_artifact() -> None:
    text = _read_text("README.md")
    payload = json.loads(
        _read_text("proofs/artifacts/lerobot_expanded_benchmarks/lerobot__columbia_cairlab_pusht_real/benchmark_result.json")
    )
    results = payload["results"]

    expected = {
        "zpe-robotics": round(results["zpe_p8"]["compression_ratio"], 2),
        "gzip -9": round(results["gzip_l9"]["compression_ratio"], 2),
        "lz4": round(results["lz4_default"]["compression_ratio"], 2),
    }
    for label, ratio in expected.items():
        assert f"| `{label}` | `{ratio:.2f}x` |" in text
