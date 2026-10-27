"""
Hashcat Rule and Mask Exporters
===============================
Generates targeted Hashcat rule files (.rule) and mask configurations (.hcmask)
for high-speed GPU cracking pipelines (Attack Modes 0 and 3).
"""

from __future__ import annotations

import datetime
import os
from typing import List


def export_hashcat_rules(filepath: str) -> None:
    """
    Generate targeted Hashcat rule set (.rule).

    Args:
        filepath: Output destination path.
    """
    rules: List[str] = [
        "# --------------------------------------------------------------------",
        "# Destroyer Targeted Hashcat Rule Set",
        f"# Generated: {datetime.datetime.now().isoformat()}",
        "# --------------------------------------------------------------------",
        ":",                    # No-op (exact word)
        "c",                    # Capitalize first letter
        "u",                    # UPPERCASE
        "l",                    # lowercase
        "r",                    # Reverse token
        "d",                    # Duplicate token
        # Temporal year appendages
        "c $2 $0 $2 $7",        # Capitalize + append 2027
        "c $2 $0 $2 $7 $!",     # Capitalize + append 2027!
        "c $2 $0 $2 $7 $@ ",    # Capitalize + append 2027@
        "c $2 $0 $2 $7 $#",     # Capitalize + append 2027#
        "c $2 $0 $2 $6",        # Capitalize + append 2026
        "c $2 $0 $2 $6 $!",     # Capitalize + append 2026!
        "c $2 $0 $2 $6 $@ ",    # Capitalize + append 2026@
        "c $2 $0 $2 $5 $!",     # Capitalize + append 2025!
        "c $2 $0 $2 $8 $!",     # Capitalize + append 2028!
        "c $2 $7 $!",           # Capitalize + append 27!
        "c $2 $6 $!",           # Capitalize + append 26!
        # Special symbol and numeric padding
        "c $! $@ $#",           # Capitalize + append !@#
        "c $1 $2 $3 $!",        # Capitalize + append 123!
        "^! c",                 # Prepend ! + Capitalize
        "^@ c",                 # Prepend @ + Capitalize
        # Selective leetspeak mutations
        "sa@",                  # Replace 'a' with '@'
        "se3",                  # Replace 'e' with '3'
        "so0",                  # Replace 'o' with '0'
        "si1",                  # Replace 'i' with '1'
        "sa@ se3 si1 so0",      # Compound selective leet
        "c sa@ se3 si1 so0 $!", # Capitalize + selective leet + append '!'
        "c sa@ se3 si1 so0 $2 $0 $2 $7 $!", # Capitalize + selective leet + append '2027!'
    ]

    target_dir = os.path.dirname(os.path.abspath(filepath))
    if target_dir and not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as fh:
        fh.write("\n".join(rules) + "\n")


def export_hashcat_masks(filepath: str) -> None:
    """
    Generate targeted Hashcat mask configuration file (.hcmask).

    Args:
        filepath: Output destination path.
    """
    masks: List[str] = [
        "# --------------------------------------------------------------------",
        "# Destroyer Targeted Hashcat Mask File (.hcmask)",
        f"# Generated: {datetime.datetime.now().isoformat()}",
        "# --------------------------------------------------------------------",
        "?u?l?l?l?l2027!",
        "?u?l?l?l?l?l2027!",
        "?u?l?l?l?l?l?l2027!",
        "?u?l?l?l?l2026!",
        "?u?l?l?l?l?l2026!",
        "?u?l?l?l?l?l?l2026!",
        "?u?l?l?l?l2027@",
        "?u?l?l?l?l?l2027@",
        "?u?l?l?l?l2027#",
        "?u?l?l?l?l?l2027#",
        "?u?l?l?l?l?l?l?d?d?s",
        "?u?l?l?l?l?l?d?d?d?s",
        "?s?u?l?l?l?l?l?d?d?d?d",
        "?u?l?l?l?l?l123!",
        "?u?l?l?l?l?l?l123!",
    ]

    target_dir = os.path.dirname(os.path.abspath(filepath))
    if target_dir and not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as fh:
        fh.write("\n".join(masks) + "\n")
