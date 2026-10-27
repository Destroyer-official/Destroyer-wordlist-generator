"""
Configuration Loader
====================
Parses and validates INI configuration files for the Destroyer package.
"""

from __future__ import annotations

import configparser
import os
from typing import Any, Dict, List, Optional


class AppConfig:
    """Strongly typed application configuration container."""

    def __init__(self, raw_config: Optional[Dict[str, Any]] = None) -> None:
        raw = raw_config or {}
        self.years: List[str] = raw.get("years", [str(y) for y in range(1950, 2031)])
        self.short_years: List[str] = raw.get("short_years", [
            "24", "25", "26", "27", "28", "29", "30", "95", "96", "97", "98", "99",
            "00", "01", "02", "03", "04", "05", "10", "15", "20", "21", "22", "23"
        ])
        self.seasons: List[str] = raw.get("seasons", ["Spring", "Summer", "Autumn", "Fall", "Winter"])
        self.quarters: List[str] = raw.get("quarters", ["Q1", "Q2", "Q3", "Q4", "H1", "H2", "FY24", "FY25", "FY26", "FY27", "FY28"])
        self.months: List[str] = raw.get("months", [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ])
        self.short_months: List[str] = raw.get("short_months", [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
        ])
        self.walks: List[str] = raw.get("walks", ["123456", "12345678", "qweasd", "asdfgh", "zaq12wsx", "!@#$", "!@#$%^"])
        self.chars: List[str] = raw.get("chars", ["!", "@", "#", "$", "%", "&", "*", "-", "_", "=", "+", "?", "~"])
        self.separators: List[str] = raw.get("separators", ["-", "_", ".", "@", "#", "$", "!"])
        self.num_from: int = raw.get("num_from", 0)
        self.num_to: int = raw.get("num_to", 100)
        self.wcfrom: int = raw.get("wcfrom", 8)
        self.wcto: int = raw.get("wcto", 64)
        self.min_passphrase_length: int = raw.get("min_passphrase_length", 15)
        self.max_passphrase_length: int = raw.get("max_passphrase_length", 64)
        self.user_agent: str = raw.get("user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        self.scraper_timeout: int = raw.get("scraper_timeout", 10)
        self.scraper_max_words: int = raw.get("scraper_max_words", 50)
        self.leet_map: Dict[str, str] = raw.get("leet_map", {
            "a": "4", "i": "1", "e": "3", "t": "7", "o": "0", "s": "5", "g": "9", "z": "2", "b": "8"
        })


def load_configuration(filename: Optional[str] = None) -> AppConfig:
    """
    Parse configuration from an INI file. Falls back to default values if not found.

    Args:
        filename: Optional path to an INI configuration file.

    Returns:
        AppConfig populated with settings.
    """
    config = configparser.ConfigParser(interpolation=None)

    resolved_path = filename
    if not resolved_path:
        # Search current working directory and parent paths for destroyer.cfg
        candidates = [
            os.path.join(os.getcwd(), "destroyer.cfg"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "destroyer.cfg"),
        ]
        for c in candidates:
            if os.path.isfile(c):
                resolved_path = c
                break

    if resolved_path and os.path.isfile(resolved_path):
        config.read(resolved_path, encoding="utf-8")

    def _csv_list(section: str, key: str, fallback: List[str]) -> List[str]:
        val = config.get(section, key, fallback=",".join(fallback))
        return [item.strip() for item in val.replace(".", ",").split(",") if item.strip()]

    cycle_sec = "corporate_cycles" if config.has_section("corporate_cycles") else "corporate_seasons"

    years = _csv_list("years", "years", [str(y) for y in range(1950, 2031)])
    short_years = _csv_list("years", "short_years", ["24", "25", "26", "27", "28", "29", "30"])
    seasons = _csv_list(cycle_sec, "seasons", ["Spring", "Summer", "Autumn", "Fall", "Winter"])
    quarters = _csv_list(cycle_sec, "quarters", ["Q1", "Q2", "Q3", "Q4", "H1", "H2", "FY24", "FY25", "FY26", "FY27", "FY28"])
    months = _csv_list(cycle_sec, "months", [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ])
    short_months = _csv_list(cycle_sec, "short_months", ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    walks = _csv_list("keyboard_walks", "walks", ["123456", "12345678", "qweasd", "asdfgh", "zaq12wsx", "!@#$", "!@#$%^"])
    chars = _csv_list("specialchars", "chars", ["!", "@", "#", "$", "%", "&", "*", "-", "_", "=", "+", "?", "~"])
    separators = _csv_list("separators", "separators", ["-", "_", ".", "@", "#", "$", "!"])

    num_from = config.getint("nums", "from", fallback=0)
    num_to = config.getint("nums", "to", fallback=100)

    shaping_sec = "shaping" if config.has_section("shaping") else "nums"
    wcfrom = config.getint(shaping_sec, "wcfrom", fallback=8)
    wcto = config.getint(shaping_sec, "wcto", fallback=64)

    min_pass = config.getint("nist", "min_passphrase_length", fallback=15)
    max_pass = config.getint("nist", "max_passphrase_length", fallback=64)

    user_agent = config.get("scraper", "user_agent", fallback="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    scraper_timeout = config.getint("scraper", "timeout", fallback=10)
    scraper_max_words = config.getint("scraper", "max_words", fallback=50)

    leet_map: Dict[str, str] = {}
    if config.has_section("leet"):
        for k, v in config.items("leet"):
            leet_map[k.lower()] = v
    else:
        leet_map = {"a": "4", "i": "1", "e": "3", "t": "7", "o": "0", "s": "5", "g": "9", "z": "2", "b": "8"}

    return AppConfig({
        "years": years,
        "short_years": short_years,
        "seasons": seasons,
        "quarters": quarters,
        "months": months,
        "short_months": short_months,
        "walks": walks,
        "chars": chars,
        "separators": separators,
        "num_from": num_from,
        "num_to": num_to,
        "wcfrom": wcfrom,
        "wcto": wcto,
        "min_passphrase_length": min_pass,
        "max_passphrase_length": max_pass,
        "user_agent": user_agent,
        "scraper_timeout": scraper_timeout,
        "scraper_max_words": scraper_max_words,
        "leet_map": leet_map,
    })
