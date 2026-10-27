"""
Keyboard Walk Generator
=======================
Generates candidates using physical keyboard sequence patterns and walks.
"""

from __future__ import annotations

from typing import Generator, List
from destroyer.config import AppConfig


class KeyboardWalkGenerator:
    """Implements spatial keyboard sequence template T9."""

    def __init__(self, base_tokens: List[str], config: AppConfig) -> None:
        self.base_tokens: List[str] = [t for t in base_tokens if len(t) >= 2]
        self.cfg: AppConfig = config

    def generate(self) -> Generator[str, None, None]:
        """Stream keyboard walk combinations."""
        walks = self.cfg.walks

        for token in self.base_tokens:
            variants = [token.capitalize(), token.lower()]
            for var in variants:
                for walk in walks:
                    yield f"{var}{walk}"
                    yield f"{walk}{var}"
                    yield f"{var}!{walk}"
