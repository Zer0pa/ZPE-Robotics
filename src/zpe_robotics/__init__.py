"""zpe-robotics package surface."""

from importlib.metadata import PackageNotFoundError, version as distribution_version
from pathlib import Path
import tomllib

from .codec import ZPBotCodec
from .release_candidate import REFERENCE_ROUNDTRIP_SHA256


def _pyproject_version() -> str:
    pyproject_path = Path(__file__).resolve().parents[2] / "pyproject.toml"
    if not pyproject_path.exists():
        return "0.0.0+unknown"
    with pyproject_path.open("rb") as handle:
        payload = tomllib.load(handle)
    project = payload.get("project", {})
    version = project.get("version")
    return str(version) if version else "0.0.0+unknown"


def _resolve_version() -> str:
    for distribution_name in ("zpe-robotics", "zpe-motion-kernel"):
        try:
            return distribution_version(distribution_name)
        except PackageNotFoundError:
            continue
    return _pyproject_version()


__version__ = _resolve_version()

__all__ = ["REFERENCE_ROUNDTRIP_SHA256", "ZPBotCodec", "__version__"]
