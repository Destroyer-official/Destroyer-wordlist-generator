"""
John the Ripper Rule Exporter
=============================
Generates targeted rule files compatible with John the Ripper (john.conf / rules).
"""

from __future__ import annotations

import datetime
import os
from typing import List


def export_john_rules(filepath: str) -> None:
    """
    Generate targeted John the Ripper rule set.

    Args:
        filepath: Output destination path.
    """
    rules: List[str] = [
        "# --------------------------------------------------------------------",
        "# Destroyer Targeted John the Ripper Rule Set",
        f"# Generated: {datetime.datetime.now().isoformat()}",
        "# --------------------------------------------------------------------",
        "[List.Rules:Destroyer]",
        ":",                    # As-is
        "c",                    # Capitalize
        "u",                    # Upper
        "l",                    # Lower
        "c $2 $0 $2 $7",        # Capitalize + 2027
        "c $2 $0 $2 $7 $!",     # Capitalize + 2027!
        "c $2 $0 $2 $6 $!",     # Capitalize + 2026!
        "c $2 $0 $2 $5 $!",     # Capitalize + 2025!
        "c $2 $0 $2 $8 $!",     # Capitalize + 2028!
        "c $1 $2 $3 $!",        # Capitalize + 123!
        "^! c",                 # Prepend ! + Capitalize
        "sa@ se3 si1 so0",      # Selective leet
    ]

    target_dir = os.path.dirname(os.path.abspath(filepath))
    if target_dir and not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as fh:
        fh.write("\n".join(rules) + "\n")
