"""
Leetspeak & Mangling Engine
===========================
Executes selective, single-character, and full character substitution transforms.
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

    def _apply_selective_leet(self, token: str) -> List[str]:
        """
        Generate high-probability selective mutations:
        1. All light substitutions (e->3, a->@, o->0, i->1, s->$)
        2. Individual single-letter substitutions (e.g. only 'a'->'@' or only 'o'->'0')
        """
        variants: Set[str] = set()
        light_map = {"e": "3", "a": "@", "o": "0", "i": "1", "s": "$"}

        # 1. Full light conversion
        chars = list(token)
        for idx, char in enumerate(chars):
            cl = char.lower()
            if cl in light_map:
                chars[idx] = light_map[cl]
        full_light = "".join(chars)
        if full_light != token:
            variants.add(full_light)

        # 2. Individual letter class mutations
        token_lower = token.lower()
        for letter, replacement in light_map.items():
            if letter in token_lower:
                single_mutated = token_lower.replace(letter, replacement)
                if single_mutated != token_lower:
                    variants.add(single_mutated)

        return list(variants)

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

            for selective in self._apply_selective_leet(token):
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
