"""
Corporate & Directory Rollover Generator
========================================
Generates candidates matching enterprise Active Directory, Azure AD, and Okta
periodic rotation patterns: seasons, quarters, months, and administrative tokens.
"""

from __future__ import annotations

from typing import Generator, List
from destroyer.config import AppConfig


class CorporateGenerator:
    """Implements enterprise rotation templates T5 and T6."""

    def __init__(self, corporate_tokens: List[str], config: AppConfig) -> None:
        self.corporate_tokens: List[str] = [t for t in corporate_tokens if t]
        self.cfg: AppConfig = config

    def generate(self) -> Generator[str, None, None]:
        """Stream enterprise and directory rollover candidates."""
        years = ["2027", "2026", "2025", "2028", "2024"]
        special_chars = self.cfg.chars
        seasons = self.cfg.seasons
        quarters = self.cfg.quarters
        months = self.cfg.months
        short_months = self.cfg.short_months

        admin_words = ["Welcome", "Admin", "Password"]
        active_corp_tokens = list(dict.fromkeys(self.corporate_tokens + admin_words))

        # Organization / System tokens + Year + Punctuation
        for cw in active_corp_tokens:
            cw_cap = cw.capitalize()
            for yr in years:
                for sym in special_chars[:8]:
                    yield f"{cw_cap}{yr}{sym}"
                    yield f"{cw_cap}@{yr}"
                    yield f"{cw_cap}#{yr}"
                    yield f"{cw_cap}!{yr}"
                    yield f"{cw_cap}{sym}{yr}"
                    yield f"{sym}{cw_cap}{yr}"

        # Seasons + Year + Symbol
        for season in seasons:
            for yr in years[:4]:
                for sym in ["!", "@", "#", "$", "*"]:
                    yield f"{season}{yr}{sym}"
                    yield f"{season}{sym}{yr}"
                    yield f"{season}{yr}"
                    yield f"{season.lower()}{yr}{sym}"

        # Months + Year + Symbol (Active Directory monthly resets)
        for month in (months + short_months):
            for yr in years[:4]:
                for sym in ["!", "@", "#", "$"]:
                    yield f"{month}{yr}{sym}"
                    yield f"{month}@{yr}"
                    yield f"{month}#{yr}"

        # Fiscal quarters
        for qtr in quarters:
            for yr in ["2027", "2026", "2025", "2028", "27", "26"]:
                for sym in ["!", "@", "#", "$"]:
                    yield f"{qtr}{yr}{sym}"
                    yield f"{qtr}@{yr}"
