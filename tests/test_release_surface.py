from __future__ import annotations

from pathlib import Path
import re
import tomllib


ROOT = Path(__file__).resolve().parents[1]
CURRENT_DOC_SURFACE = [
    "CHANGELOG.md",
    "docs/ARCHITECTURE.md",
    "docs/CLAIM_BOUNDARY.md",
    "docs/LEGAL_BOUNDARIES.md",
    "docs/MECHANICS_LAYER.md",
    "docs/OPERATOR_RUNBOOK.md",
    "docs/family/ROBOTICS_RELEASE_LINKAGE.md",
]
CURRENT_FRONTDOOR_DOCS = [
    "README.md",
    "docs/ARCHITECTURE.md",
    "docs/CLAIM_BOUNDARY.md",
    "docs/LEGAL_BOUNDARIES.md",
    "docs/MECHANICS_LAYER.md",
    "docs/OPERATOR_RUNBOOK.md",
    "docs/family/ROBOTICS_RELEASE_LINKAGE.md",
]


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


def test_license_uses_three_year_change_date() -> None:
    text = _read_text("LICENSE")
    assert "three (3) years after the date of first public release" in text


def test_root_readme_keeps_expected_gif_surface() -> None:
    text = _read_text("README.md")
    gif_refs = re.findall(r'\.github/assets/readme/[^"]+\.gif', text)
    assert gif_refs == [
        ".github/assets/readme/zpe-masthead.gif",
        ".github/assets/readme/zpe-masthead-option-3-2.gif",
        ".github/assets/readme/zpe-masthead-option-3-3.gif",
    ]


def test_docs_surface_uses_shared_masthead_only() -> None:
    for relative_path in CURRENT_DOC_SURFACE:
        assert (ROOT / relative_path).exists(), relative_path
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
    banned_phrases = [
        "private repository",
        "private staging only",
        "private github repo",
    ]

    for relative_path in CURRENT_FRONTDOOR_DOCS:
        assert (ROOT / relative_path).exists(), relative_path
        text = _read_text(relative_path).lower()
        for phrase in banned_phrases:
            assert phrase not in text, f"{relative_path} contains {phrase!r}"
