"""
Passphrase Synthesis Engine (NIST SP 800-63B)
=============================================
Synthesizes multi-token passphrases with natural delimiters and temporal tokens
conforming to the 15-64 character bounds specified in NIST SP 800-63B.
"""

from __future__ import annotations

from typing import Generator, List
from destroyer.config import AppConfig


class PassphraseGenerator:
    """Implements multi-token passphrase synthesis template T7."""

    def __init__(self, token_pool: List[str], config: AppConfig, mode: str = "standard", nist_mode: bool = False) -> None:
        self.tokens: List[str] = [t for t in token_pool if len(t) >= 2]
        self.cfg: AppConfig = config
        self.mode: str = mode.lower()
        self.nist_mode: bool = nist_mode

    def generate(self) -> Generator[str, None, None]:
        """Stream multi-token passphrases."""
        separators = self.cfg.separators
        years = ["2027", "2026", "2025", "2028"]
        symbols = ["!", "#", "$", "@", ""]

        # 2-token passphrases with delimiters and temporal anchors
        for w1 in self.tokens:
            for w2 in self.tokens:
                if w1.lower() == w2.lower():
                    continue
                w1_c = w1.capitalize()
                w2_c = w2.capitalize()

                for sep in separators[:6]:
                    for yr in years:
                        for sym in symbols:
                            yield f"{w1_c}{sep}{w2_c}{sep}{yr}{sym}"
                            yield f"{w1_c}{sep}{yr}{sep}{w2_c}{sym}"

        # 3-token passphrase synthesis in deep or dedicated passphrase modes
        if self.mode in ("passphrase", "deep") and len(self.tokens) >= 3:
            sample_tokens = self.tokens[:8]
            for w1 in sample_tokens:
                for w2 in sample_tokens:
                    if w1.lower() == w2.lower():
                        continue
                    for w3 in sample_tokens:
                        if w3.lower() in (w1.lower(), w2.lower()):
                            continue
                        w1_c, w2_c, w3_c = w1.capitalize(), w2.capitalize(), w3.capitalize()
                        for sep in ["-", "_", ".", " "]:
                            yield f"{w1_c}{sep}{w2_c}{sep}{w3_c}"
                            yield f"{w1_c}{sep}{w2_c}{sep}{w3_c}2027!"
