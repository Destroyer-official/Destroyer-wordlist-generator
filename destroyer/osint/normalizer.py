"""
OSINT Token Normalization
=========================
Cleans, normalizes, and filters tokens gathered during reconnaissance.
"""

from __future__ import annotations

import re
from typing import List, Set

STOP_WORDS: Set[str] = {
    "about", "above", "across", "after", "again", "against", "all", "almost", "alone",
    "along", "already", "also", "although", "always", "among", "and", "another", "any",
    "are", "area", "around", "back", "because", "been", "before", "being", "best",
    "better", "between", "both", "business", "came", "cannot", "case", "certain",
    "clear", "come", "could", "different", "does", "done", "down", "during", "each",
    "early", "either", "enough", "even", "ever", "every", "find", "first", "four",
    "from", "full", "further", "gave", "general", "give", "given", "good", "great",
    "group", "have", "here", "high", "home", "important", "into", "just", "keep",
    "kind", "knew", "know", "large", "last", "later", "least", "less", "like", "made",
    "make", "many", "more", "most", "much", "must", "name", "need", "never", "next",
    "only", "open", "order", "other", "part", "place", "point", "possible", "present",
    "problem", "quite", "rather", "really", "right", "room", "said", "same", "several",
    "shall", "should", "side", "since", "small", "some", "state", "still", "such",
    "sure", "take", "taken", "than", "that", "the", "their", "them", "then", "there",
    "these", "they", "thing", "think", "this", "those", "though", "three", "through",
    "today", "together", "under", "until", "upon", "want", "well", "went", "were",
    "what", "when", "where", "which", "while", "white", "whole", "will", "with",
    "without", "word", "work", "world", "would", "year", "your"
}


def normalize_token(token: str) -> str:
    """Strip extraneous non-alphanumeric punctuation and lowercase."""
    return re.sub(r"[^\w\s-]", "", token).strip().lower()


def filter_tokens(raw_tokens: List[str], min_length: int = 4, max_length: int = 25) -> List[str]:
    """
    Sanitize and filter token list against stop-words and length bounds.

    Args:
        raw_tokens: Raw string tokens.
        min_length: Minimum acceptable token character length.
        max_length: Maximum acceptable token character length.

    Returns:
        List of sanitized, unique, valid tokens.
    """
    valid: Set[str] = set()
    for raw in raw_tokens:
        clean = normalize_token(raw)
        if min_length <= len(clean) <= max_length and clean not in STOP_WORDS and not clean.isdigit():
            valid.add(clean)
    return sorted(valid)
