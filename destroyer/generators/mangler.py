"""
Leetspeak & Mangling Engine
===========================
Executes selective, phonetic, and full character substitution transforms.
"""

from __future__ import annotations

from typing import Dict, Generator, List, Set
from destroyer.config import AppConfig


class ManglerGenerator:
    """Implements leetspeak mutation template T10."""

    def __init__(self, base_tokens: List[str], config: AppConfig, mode: str = "light") -> None:
        self.base_tokens: List[str] = [t for t in base_tokens if len(t) >= 2]
        self.cfg: AppConfig = config
        self.mode: str = mode.lower()

    def _apply_selective_leet(self, token: str) -> str:
        """Replace only high-frequency substitutions: e->3, a->@, o->0, i->1, s->$."""
        light_map = {"e": "3", "a": "@", "o": "0", "i": "1", "s": "$"}
        chars = list(token)
        for idx, char in enumerate(chars):
            cl = char.lower()
            if cl in light_map:
                chars[idx] = light_map[cl]
        return "".join(chars)

    def _apply_full_leet(self, token: str) -> str:
        """Replace all characters present in configuration leet map."""
        res = token
        for letter, replacement in self.cfg.leet_map.items():
            res = res.replace(letter, replacement).replace(letter.upper(), replacement)
        return res

    def generate(self) -> Generator[str, None, None]:
        """Stream leetspeak mutated candidates."""
        if self.mode == "off":
            return

        years = ["2027", "2026", "2025", "123", "01"]
        symbols = ["!", "@", "#", "$", ""]

        for token in self.base_tokens:
            mutations: Set[str] = set()

            selective = self._apply_selective_leet(token)
            if selective != token:
                mutations.add(selective)

            if self.mode == "standard":
                full = self._apply_full_leet(token)
                if full != token:
                    mutations.add(full)

            for mutated in mutations:
                yield mutated
                for yr in years:
                    for sym in symbols:
                        yield f"{mutated}{yr}{sym}"
                        yield f"{mutated.capitalize()}{yr}{sym}"
