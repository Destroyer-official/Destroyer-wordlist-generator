"""
PCFG Candidate Generator
========================
Generates password candidates using Probabilistic Context-Free Grammar (PCFG)
production templates combining entity tokens, calendar years, sequences, and symbols.
"""

from __future__ import annotations

from typing import Generator, List
from destroyer.config import AppConfig


def casing_permutations(token: str, include_upper: bool = True) -> List[str]:
    """Generate casing permutations: Title, lower, and optionally UPPER."""
    if not token:
        return []
    variants = [token.capitalize(), token.lower()]
    if include_upper:
        variants.append(token.upper())
    return list(dict.fromkeys(variants))


class PCFGGenerator:
    """Implements structural PCFG templates T1, T2, T3, T4, and T8."""

    def __init__(self, primary_tokens: List[str], date_tokens: List[str], config: AppConfig, mode: str = "standard") -> None:
        self.primary_tokens: List[str] = primary_tokens
        self.date_tokens: List[str] = date_tokens
        self.cfg: AppConfig = config
        self.mode: str = mode.lower()

    def generate(self) -> Generator[str, None, None]:
        """Stream candidates adhering to PCFG structural templates."""
        priority_years = ["2027", "2026", "2025", "2024", "2028", "2029", "2030", "2023", "2022", "2020"]
        if self.mode == "deep":
            years = list(dict.fromkeys(priority_years + self.cfg.years))
        else:
            years = list(dict.fromkeys(priority_years + self.cfg.years[:30]))

        short_years = self.cfg.short_years
        special_chars = self.cfg.chars
        sequences = ["123", "1234", "12345", "123456", "01", "007", "777", "999"]
        include_upper = self.mode in ("standard", "deep")

        for token in self.primary_tokens:
            for variant in casing_permutations(token, include_upper=include_upper):
                # Template 1 & 3: Word + Year + Symbol / Word + Symbol + Year
                for yr in years:
                    yield f"{variant}{yr}"
                    for sym in special_chars[:8]:
                        yield f"{variant}{yr}{sym}"
                        yield f"{variant}{sym}{yr}"
                        yield f"{sym}{variant}{yr}"

                # 2-digit years
                for sy in short_years:
                    yield f"{variant}{sy}"
                    for sym in special_chars[:6]:
                        yield f"{variant}{sy}{sym}"
                        yield f"{variant}@{sy}"

                # Template 4: Word + Sequence + Symbol
                for seq in sequences:
                    yield f"{variant}{seq}"
                    for sym in ["!", "@", "#", "$"]:
                        yield f"{variant}{seq}{sym}"
                        yield f"{variant}{sym}{seq}"

                # Template 8: Word + Date Component
                for dt in self.date_tokens:
                    yield f"{variant}{dt}"
                    yield f"{dt}{variant}"
                    for sym in ["!", "@", "#", "_"]:
                        yield f"{variant}{sym}{dt}"
                        yield f"{variant}{dt}{sym}"
