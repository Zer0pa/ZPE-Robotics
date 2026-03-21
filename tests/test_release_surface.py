from __future__ import annotations

from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[1]


def _load_pyproject() -> dict[str, object]:
    with (ROOT / "pyproject.toml").open("rb") as handle:
        return tomllib.load(handle)


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
