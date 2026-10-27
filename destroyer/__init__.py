"""
Destroyer Package Initialization
================================
Targeted password list and passphrase generation engine.
"""

from __future__ import annotations

from destroyer.core.engine import DestroyerEngine
from destroyer.models.profile import TargetProfile
from destroyer.config import load_configuration

__version__ = "3.0.0"
__all__ = [
    "DestroyerEngine",
    "TargetProfile",
    "load_configuration",
    "__version__",
]
