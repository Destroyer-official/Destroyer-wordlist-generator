"""
Grammar and Pattern Models
==========================
Defines Probabilistic Context-Free Grammar (PCFG) structures and mask types.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class PCFGRule:
    """Formal definition of a candidate production template."""
    rule_id: str
    description: str
    production: str
    example: str


PCFG_PRODUCTION_CATALOG: List[PCFGRule] = [
    PCFGRule("T1", "Word + Year + Punctuation", "S -> Word(case) . Year . Symbol", "Shadow2026!"),
    PCFGRule("T2", "Punctuation + Word + Year", "S -> Symbol . Word(case) . Year", "@Shadow2027"),
    PCFGRule("T3", "Word + Punctuation + Year", "S -> Word(case) . Symbol . Year", "Shadow@2027"),
    PCFGRule("T4", "Word + Sequence + Punctuation", "S -> Word(case) . Sequence . Symbol", "Shadow123!"),
    PCFGRule("T5", "Organizational Rollover", "S -> CorpToken . Year . Symbol", "CyberCorp2027!"),
    PCFGRule("T6", "Directory Cycle Rollover", "S -> CycleToken . Year . Symbol", "Spring2027!"),
    PCFGRule("T7", "Multi-Token Passphrase", "S -> Word1 . Delim . Word2 . Delim . Year . Symbol", "Mercer-Shadow-2027!"),
    PCFGRule("T8", "Date Substring Append", "S -> Word(case) . DateComponent", "Alex14051996"),
    PCFGRule("T9", "Keyboard Walk Combination", "S -> Word(case) . Walk", "Shadow123456"),
    PCFGRule("T10", "Selective Leetspeak Mutation", "S -> Leet(Word) . Year . Symbol", "Sh@d0w2027!"),
]
