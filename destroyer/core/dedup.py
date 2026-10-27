"""
Memory-Bounded Deduplication
============================
Provides memory-safe unique candidate tracking to prevent Out-Of-Memory (OOM)
conditions when compiling high-volume candidate streams.
"""

from __future__ import annotations

from typing import Set


class MemoryBoundedDeduplicator:
    """
    In-memory deduplicator with strict capacity bounds.
    When the tracked set exceeds the capacity limit, the cache resets or slides,
    ensuring memory consumption stays strictly bounded under a deterministic threshold.
    """

    def __init__(self, capacity: int = 1_500_000) -> None:
        """
        Initialize deduplicator.

        Args:
            capacity: Maximum number of candidate hashes retained concurrently.
        """
        self.capacity: int = capacity
        self._seen: Set[str] = set()

    def is_unique(self, candidate: str) -> bool:
        """
        Check if candidate has been seen. If unique, records and returns True.

        Args:
            candidate: Candidate string to inspect.

        Returns:
            True if the candidate was unique and added, False otherwise.
        """
        if candidate in self._seen:
            return False

        self._seen.add(candidate)
        if len(self._seen) > self.capacity:
            self._seen.clear()

        return True

    def reset(self) -> None:
        """Clear all tracked entries."""
        self._seen.clear()

    def __len__(self) -> int:
        return len(self._seen)
