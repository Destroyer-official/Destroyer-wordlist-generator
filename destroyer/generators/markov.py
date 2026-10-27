"""
Markov and Statistical Transition Generator
===========================================
Generates candidate mutations based on empirical bi-gram transition probabilities
observed in credential breach datasets, producing plausible phonetic variations.
"""

from __future__ import annotations

import collections
from typing import Dict, Generator, List, Set


class MarkovTransitionGenerator:
    """
    Bi-gram Markov chain generator. Models character transition probabilities
    from input target tokens to synthesize plausible variations.
    """

    def __init__(self, seed_tokens: List[str], depth: int = 2) -> None:
        self.seed_tokens: List[str] = [t.lower() for t in seed_tokens if len(t) >= 3]
        self.depth: int = depth
        self.transitions: Dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
        self.starts: List[str] = []
        self._train()

    def _train(self) -> None:
        """Construct transition probability graph from seed tokens."""
        for token in self.seed_tokens:
            if len(token) < 2:
                continue
            self.starts.append(token[:2])
            for i in range(len(token) - 1):
                state = token[i]
                next_char = token[i + 1]
                self.transitions[state][next_char] += 1

    def generate(self, max_candidates: int = 500) -> Generator[str, None, None]:
        """Generate plausible token mutations from transition paths."""
        if not self.transitions or not self.starts:
            return

        generated: Set[str] = set()

        for start_pair in set(self.starts):
            current = start_pair
            for _ in range(4):
                last_char = current[-1]
                next_options = self.transitions.get(last_char)
                if not next_options:
                    break
                most_common_next = [char for char, _ in next_options.most_common(2)]
                for next_c in most_common_next:
                    candidate = (current + next_c).capitalize()
                    if candidate not in generated:
                        generated.add(candidate)
                        yield candidate
                        yield f"{candidate}2027!"
                        yield f"{candidate}123!"

                    if len(generated) >= max_candidates:
                        return
