"""
Destroyer Orchestration Engine
==============================
Coordinates sub-generators, applies grammatical production templates,
and manages the streaming output pipeline.
"""

from __future__ import annotations

import time
from typing import Any, Dict, Generator, List, Optional
from destroyer.config import AppConfig, load_configuration
from destroyer.core.streamer import StreamWriter
from destroyer.generators.corporate import CorporateGenerator
from destroyer.generators.keyboard import KeyboardWalkGenerator
from destroyer.generators.mangler import ManglerGenerator
from destroyer.generators.markov import MarkovTransitionGenerator
from destroyer.generators.passphrase import PassphraseGenerator
from destroyer.generators.pcfg import PCFGGenerator
from destroyer.models.profile import TargetProfile


class DestroyerEngine:
    """Master generation coordinator orchestrating all sub-generators."""

    def __init__(
        self,
        profile: TargetProfile,
        config: Optional[AppConfig] = None,
        mode: str = "standard",
        min_len: int = 8,
        max_len: int = 64,
        leet_mode: str = "light",
        include_corporate: bool = True,
        nist_mode: bool = False,
    ) -> None:
        """
        Initialize the orchestration engine.

        Args:
            profile: Populated TargetProfile instance.
            config: Optional AppConfig instance. If None, loads defaults.
            mode: Generation mode ('fast', 'standard', 'deep', 'passphrase').
            min_len: Minimum acceptable candidate length.
            max_len: Maximum acceptable candidate length.
            leet_mode: Leetspeak strategy ('off', 'light', 'standard').
            include_corporate: Whether to generate organizational directory patterns.
            nist_mode: Enforce NIST SP 800-63B minimum length bound of 15 characters.
        """
        self.profile: TargetProfile = profile
        self.cfg: AppConfig = config or load_configuration()
        self.mode: str = mode.lower()
        self.min_len: int = 15 if nist_mode else max(1, min_len)
        self.max_len: int = max(self.min_len, max_len)
        self.leet_mode: str = leet_mode.lower()
        self.include_corporate: bool = include_corporate
        self.nist_mode: bool = nist_mode

        # Token extraction
        self.primary_tokens: List[str] = self._extract_primary_tokens()
        self.secondary_tokens: List[str] = self._extract_secondary_tokens()
        self.date_tokens: List[str] = self._extract_date_tokens()

    def _extract_primary_tokens(self) -> List[str]:
        """Extract primary target entity tokens."""
        p = self.profile
        tokens: List[str] = []

        for val in [p.name, p.surname, p.nick]:
            if val:
                tokens.append(val)

        if p.name and p.surname:
            tokens.append(p.name + p.surname)
            tokens.append(p.name[0] + p.surname)
            tokens.append(p.name + "." + p.surname)
            tokens.append(p.name + "_" + p.surname)

        tokens.extend(p.handles)

        if p.email and "@" in p.email:
            tokens.append(p.email.split("@")[0])

        tokens.extend(p.keywords)
        return list(dict.fromkeys([t for t in tokens if len(t) >= 2]))

    def _extract_secondary_tokens(self) -> List[str]:
        """Extract associative and organizational context tokens."""
        p = self.profile
        tokens: List[str] = []

        for val in [p.partner_name, p.partner_nick, p.guardian_name, p.guardian_nick, p.city, p.sports_team]:
            if val:
                tokens.append(val)

        tokens.extend(p.children_names)
        tokens.extend(p.pet_names)

        if p.company:
            tokens.append(p.company)
        if p.company_acronym:
            tokens.append(p.company_acronym)
        if p.department:
            tokens.append(p.department)
        if p.domain:
            tokens.append(p.domain.split(".")[0])
        tokens.extend(p.project_names)

        return list(dict.fromkeys([t for t in tokens if len(t) >= 2]))

    def _extract_date_tokens(self) -> List[str]:
        """Extract numeric date and phone substrings."""
        tokens: List[str] = []
        p = self.profile

        for d_comp in [p.birth_components, p.partner_birth_components, p.guardian_birth_components]:
            for val in d_comp.values():
                if val:
                    tokens.append(val)

        if len(p.mobile) >= 4:
            tokens.append(p.mobile[-4:])
        if len(p.mobile) >= 6:
            tokens.append(p.mobile[-6:])
        if len(p.mobile) >= 10:
            tokens.append(p.mobile[-10:])

        return list(dict.fromkeys(tokens))

    def generate_candidates(self) -> Generator[str, None, None]:
        """
        Coordinate sub-generators to stream candidates sequentially.
        """
        all_tokens = list(dict.fromkeys(self.primary_tokens + self.secondary_tokens))

        # 1. NIST SP 800-63B Multi-Token Passphrase Generator
        passphrase_gen = PassphraseGenerator(
            token_pool=all_tokens,
            config=self.cfg,
            mode=self.mode,
            nist_mode=self.nist_mode
        )
        yield from passphrase_gen.generate()

        if self.mode == "passphrase":
            return

        # 2. Corporate & Directory Rollover Generator
        if self.include_corporate:
            corp_words = [self.profile.company, self.profile.company_acronym]
            corporate_gen = CorporateGenerator(corporate_tokens=corp_words, config=self.cfg)
            yield from corporate_gen.generate()

        # 3. PCFG Structural Template Generator
        pcfg_gen = PCFGGenerator(
            primary_tokens=self.primary_tokens,
            date_tokens=self.date_tokens,
            config=self.cfg,
            mode=self.mode
        )
        yield from pcfg_gen.generate()

        # 4. Associate Permutations
        for p_tok in self.primary_tokens:
            p_cap = p_tok.capitalize()
            for s_tok in self.secondary_tokens:
                s_cap = s_tok.capitalize()
                for sep in ["", "_", ".", "-", "@", "&"]:
                    combo = f"{p_cap}{sep}{s_cap}"
                    yield combo
                    for yr in ["2027", "2026", "2025", "123"]:
                        yield f"{combo}{yr}"
                        for sym in ["!", "@", "#"]:
                            yield f"{combo}{yr}{sym}"

        # 5. Leetspeak & Mangling Generator
        mangler_gen = ManglerGenerator(
            base_tokens=self.primary_tokens,
            config=self.cfg,
            mode=self.leet_mode
        )
        yield from mangler_gen.generate()

        # 6. Keyboard Walk Generator
        keyboard_gen = KeyboardWalkGenerator(base_tokens=self.primary_tokens, config=self.cfg)
        yield from keyboard_gen.generate()

        # 7. Statistical Markov Transition Generator (deep mode)
        if self.mode in ("deep", "standard"):
            markov_gen = MarkovTransitionGenerator(seed_tokens=self.primary_tokens)
            yield from markov_gen.generate(max_candidates=300 if self.mode == "standard" else 1500)

        # 8. Deep mode numeric suffix padding and token reversals
        if self.mode == "deep":
            for token in self.primary_tokens:
                token_cap = token.capitalize()
                for num in range(self.cfg.num_from, min(self.cfg.num_to, 200)):
                    yield f"{token_cap}{num}"
                    yield f"{token_cap}{num:02d}"
                    yield f"{token_cap}@{num}"

                rev = token[::-1]
                yield rev
                yield f"{rev}2027!"

    def execute(self, output_filepath: str) -> Dict[str, Any]:
        """
        Execute streaming generation, write to output file, and collect performance metrics.

        Args:
            output_filepath: Target destination file.

        Returns:
            Dictionary containing metrics: total words, throughput, file size,
            average entropy, and elapsed time.
        """
        start_time = time.time()
        streamer = StreamWriter(
            filepath=output_filepath,
            min_len=self.min_len,
            max_len=self.max_len,
            dedup_capacity=1_500_000
        )
        results = streamer.write_stream(self.generate_candidates())
        elapsed = time.time() - start_time

        results["elapsed_seconds"] = elapsed
        results["speed_wps"] = (results["total_words"] / elapsed) if elapsed > 0 else float(results["total_words"])
        return results
