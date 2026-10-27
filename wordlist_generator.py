#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Destroyer Wordlist Generator - Root Launcher
============================================
Backward-compatible wrapper delegating to the modular destroyer package.
"""

from __future__ import annotations

import sys
from typing import Any, Dict, List
from destroyer.cli import main as cli_main
from destroyer.config import load_configuration
from destroyer.core.engine import DestroyerEngine
from destroyer.generators.mangler import ManglerGenerator
from destroyer.models.profile import TargetProfile

CONFIG: Dict[str, Any] = {}


def read_configuration(filename: str = None) -> bool:
    """Backward-compatible configuration reader."""
    global CONFIG
    cfg = load_configuration(filename)
    CONFIG["global"] = {
        "years": cfg.years,
        "short_years": cfg.short_years,
        "seasons": cfg.seasons,
        "quarters": cfg.quarters,
        "months": cfg.months,
        "short_months": cfg.short_months,
        "walks": cfg.walks,
        "chars": cfg.chars,
        "separators": cfg.separators,
        "numfrom": cfg.num_from,
        "numto": cfg.num_to,
        "wcfrom": cfg.wcfrom,
        "wcto": cfg.wcto,
    }
    CONFIG["LEET"] = cfg.leet_map
    return True


def apply_leet_conversion(input_string: str, mode: str = "standard") -> str:
    """Backward-compatible leetspeak conversion function."""
    cfg = load_configuration()
    mangler = ManglerGenerator(base_tokens=[input_string], config=cfg, mode=mode)
    if mode == "light":
        return mangler._apply_selective_leet(input_string)
    return mangler._apply_full_leet(input_string)


def generate_wordlist_from_profile(profile_dict: Dict[str, Any], output_file: str = "passwords.txt") -> List[str]:
    """Backward-compatible API for generating wordlist from dictionary profile."""
    profile = TargetProfile.from_dict(profile_dict)
    engine = DestroyerEngine(profile=profile, mode="standard", min_len=8, max_len=64)
    engine.execute(output_file)

    with open(output_file, "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh]


def main() -> None:
    """Forward execution to the modular CLI interface."""
    cli_main()


if __name__ == "__main__":
    sys.exit(main() or 0)
