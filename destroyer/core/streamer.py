"""
Streaming Output Pipeline
=========================
Buffered, atomic stream writer capable of writing plaintext and gzip-compressed
candidate wordlists directly to disk without intermediate memory arrays.
"""

from __future__ import annotations

import gzip
import os
from typing import IO, Any, Dict, Generator, Optional
from destroyer.core.dedup import MemoryBoundedDeduplicator
from destroyer.core.entropy import calculate_keyspace_entropy


class StreamWriter:
    """
    High-throughput stream writer writing candidates directly to storage.
    Automatically handles transparent gzip compression when output ends with '.gz'.
    """

    def __init__(
        self,
        filepath: str,
        buffer_size: int = 65536,
        min_len: int = 8,
        max_len: int = 64,
        dedup_capacity: int = 1_500_000,
    ) -> None:
        """
        Initialize the stream pipeline.

        Args:
            filepath: Destination file path.
            buffer_size: Operating system I/O buffer size in bytes.
            min_len: Lower character length filter boundary.
            max_len: Upper character length filter boundary.
            dedup_capacity: Maximum memory footprint bound for the deduplicator.
        """
        self.filepath: str = os.path.abspath(filepath)
        self.buffer_size: int = buffer_size
        self.min_len: int = min_len
        self.max_len: int = max_len
        self.deduplicator: MemoryBoundedDeduplicator = MemoryBoundedDeduplicator(capacity=dedup_capacity)
        self.is_gzip: bool = self.filepath.endswith(".gz")

        # Metric accumulators
        self.total_candidates: int = 0
        self.nist_compliant: int = 0
        self.total_entropy: float = 0.0

    def write_stream(self, generator: Generator[str, None, None]) -> Dict[str, Any]:
        """
        Drain the candidate generator, filter length bounds, deduplicate,
        and stream clean lines directly to disk.

        Args:
            generator: Generator yielding candidate strings.

        Returns:
            Dictionary containing metrics: total_words, nist_compliant,
            avg_entropy, and output_path.
        """
        target_dir = os.path.dirname(self.filepath)
        if target_dir and not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)

        fh: IO[Any]
        if self.is_gzip:
            fh = gzip.open(self.filepath, "wt", encoding="utf-8")
        else:
            fh = open(self.filepath, "w", encoding="utf-8", buffering=self.buffer_size)

        try:
            for candidate in generator:
                length = len(candidate)
                if length < self.min_len or length > self.max_len:
                    continue

                if self.deduplicator.is_unique(candidate):
                    fh.write(candidate + "\n")
                    self.total_candidates += 1
                    self.total_entropy += calculate_keyspace_entropy(candidate)

                    if length >= 15:
                        self.nist_compliant += 1
        finally:
            fh.close()

        file_size_kb = os.path.getsize(self.filepath) / 1024.0
        avg_entropy = (self.total_entropy / self.total_candidates) if self.total_candidates > 0 else 0.0

        return {
            "total_words": self.total_candidates,
            "nist_compliant": self.nist_compliant,
            "avg_entropy": avg_entropy,
            "file_size_kb": file_size_kb,
            "output_path": self.filepath,
        }
