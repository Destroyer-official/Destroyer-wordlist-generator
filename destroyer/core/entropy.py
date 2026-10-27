"""
Entropy and Cryptographic Strength Analysis
===========================================
Provides mathematical measures of password keyspace cardinality,
theoretical entropy in bits, and estimated offline brute-force cracking resistance.
"""

from __future__ import annotations

import collections
import math
from typing import Dict


def calculate_keyspace_entropy(candidate: str) -> float:
    """
    Compute theoretical keyspace entropy in bits based on character pool cardinality.

    Formula:
        H = L * log2(|R|)
    where L is length and |R| is the size of character classes present.

    Args:
        candidate: Plaintext candidate string.

    Returns:
        Entropy in bits.
    """
    if not candidate:
        return 0.0

    has_lower = any(c.islower() for c in candidate)
    has_upper = any(c.isupper() for c in candidate)
    has_digit = any(c.isdigit() for c in candidate)
    has_symbol = any(not c.isalnum() for c in candidate)

    cardinality = 0
    if has_lower:
        cardinality += 26
    if has_upper:
        cardinality += 26
    if has_digit:
        cardinality += 10
    if has_symbol:
        cardinality += 33

    cardinality = max(cardinality, 2)
    return len(candidate) * math.log2(cardinality)


def calculate_shannon_entropy(candidate: str) -> float:
    """
    Compute exact Shannon information entropy based on character frequency distribution.

    Formula:
        H = - sum(p(x) * log2(p(x)))
    where p(x) is the empirical probability of character x.

    Args:
        candidate: Plaintext candidate string.

    Returns:
        Shannon entropy in bits per character.
    """
    if not candidate:
        return 0.0

    length = len(candidate)
    frequencies = collections.Counter(candidate)
    entropy = 0.0

    for count in frequencies.values():
        probability = count / length
        entropy -= probability * math.log2(probability)

    return entropy * length


def estimate_crack_time(entropy_bits: float, hash_rate: float = 100_000_000_000.0) -> str:
    """
    Estimate offline recovery duration against an attacker rig with the given hash rate.
    Default hash rate: 100 GH/s (approx. dual high-end GPU cluster on fast hash like NTLM).

    Args:
        entropy_bits: Theoretical keyspace entropy in bits.
        hash_rate: Hash computations per second.

    Returns:
        Human-readable time estimate string.
    """
    if entropy_bits <= 0:
        return "Instant"

    total_combinations = 2.0 ** entropy_bits
    # Average combinations required for 50% crack probability
    average_attempts = total_combinations / 2.0
    seconds = average_attempts / max(hash_rate, 1.0)

    if seconds < 1.0:
        return "< 1 second"
    if seconds < 60.0:
        return f"{seconds:.1f} seconds"
    if seconds < 3600.0:
        return f"{seconds / 60.0:.1f} minutes"
    if seconds < 86400.0:
        return f"{seconds / 3600.0:.1f} hours"
    if seconds < 31536000.0:
        return f"{seconds / 86400.0:.1f} days"
    years = seconds / 31536000.0
    if years < 1000.0:
        return f"{years:.1f} years"
    return f"{years:.1e} years"
