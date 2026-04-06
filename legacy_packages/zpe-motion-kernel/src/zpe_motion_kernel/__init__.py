"""Deprecated compatibility package for the zpe-motion-kernel rename."""

from __future__ import annotations

import warnings


__version__ = "0.1.1"

warnings.warn(
    "zpe-motion-kernel has been renamed to zpe-robotics. Install: pip install zpe-robotics",
    DeprecationWarning,
    stacklevel=2,
)
