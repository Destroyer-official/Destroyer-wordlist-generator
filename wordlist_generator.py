#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
  ██████╗ ███████╗███████╗████████╗██████╗  ██████╗ ██╗   ██╗███████╗██████╗ 
  ██╔══██╗██╔════╝██╔════╝╚══██╔══╝██╔══██╗██╔═══██╗╚██╗ ██╔╝██╔════╝██╔══██╗
  ██║  ██║█████╗  ███████╗   ██║   ██████╔╝██║   ██║ ╚████╔╝ █████╗  ██████╔╝
  ██║  ██║██╔══╝  ╚════██║   ██║   ██╔══██╗██║   ██║  ╚██╔╝  ██╔══╝  ██╔══██╗
  ██████╔╝███████╗███████║   ██║   ██║  ██║╚██████╔╝   ██║   ███████╗██║  ██║
  ╚═════╝ ╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚══════╝╚═╝  ╚═╝
================================================================================
Destroyer Wordlist Generator
============================
A targeted wordlist and passphrase generation utility designed for authorized
penetration testing, security auditing, and password policy validation.

Architecture & Functional Modules:
----------------------------------
1. TargetProfile:
   Data container and serialization layer for target demographic, associate,
   organizational, and contextual parameters extracted during reconnaissance.

2. DestroyerGenerator:
   Core combinatorial engine employing Probabilistic Context-Free Grammar (PCFG)
   structures, temporal rollovers, selective leetspeak transforms, multi-token
   passphrase synthesis, and memory-bounded streaming deduplication.

3. Scraper (HTMLTextExtractor / scrape_url_keywords):
   Lightweight, dependency-free HTTP harvester extracting high-frequency
   contextual keywords from organizational web endpoints with stop-word filtering.

4. Rule & Mask Exporters:
   Generates targeted rule files (.rule) and mask configurations (.hcmask)
   compatible with Hashcat and John the Ripper GPU cracking pipelines.

5. Metrics:
   Calculates theoretical keyspace entropy in bits:
       H = L * log2(|R|)
   where L is candidate length and |R| is the active character pool size.
"""

from __future__ import annotations

import argparse
import collections
import configparser
import datetime
import html.parser
import json
import math
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
from typing import Any, Dict, Generator, List, Optional, Set

# Optional Rich library for structured terminal rendering
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None

# Global configuration dictionary for backward compatibility
CONFIG: Dict[str, Any] = {}

# Standard ANSI escape codes for basic terminal formatting
C_RED = "\033[1;31m"
C_GREEN = "\033[1;32m"
C_YELLOW = "\033[1;33m"
C_CYAN = "\033[1;36m"
C_RESET = "\033[0m"
C_BOLD = "\033[1m"

# Standard English stop-words filtered during web reconnaissance
STOP_WORDS: Set[str] = {
    "about", "above", "across", "after", "again", "against", "all", "almost", "alone",
    "along", "already", "also", "although", "always", "among", "and", "another", "any",
    "anybody", "anyone", "anything", "anywhere", "are", "area", "areas", "around", "ask",
    "asked", "asking", "asks", "away", "back", "backed", "backing", "backs", "became",
    "because", "become", "becomes", "becoming", "been", "before", "began", "behind",
    "being", "beings", "best", "better", "between", "both", "business", "came", "cannot",
    "case", "cases", "certain", "certainly", "clear", "clearly", "come", "could", "did",
    "differ", "different", "differently", "does", "done", "down", "downed", "downing",
    "downs", "during", "each", "early", "either", "end", "ended", "ending", "ends",
    "enough", "even", "evenly", "ever", "every", "everybody", "everyone", "everything",
    "everywhere", "face", "faces", "fact", "facts", "far", "felt", "few", "fewer", "find",
    "finds", "first", "for", "four", "from", "full", "fully", "further", "furthered",
    "furthering", "furthers", "gave", "general", "generally", "get", "gets", "give",
    "given", "gives", "going", "good", "goods", "got", "great", "greater", "greatest",
    "group", "grouped", "grouping", "groups", "had", "has", "have", "having", "her",
    "here", "herself", "high", "higher", "highest", "him", "himself", "his", "how",
    "however", "important", "interest", "interested", "interesting", "interests", "into",
    "its", "itself", "just", "keep", "keeps", "kind", "knew", "know", "known", "knows",
    "large", "largely", "last", "later", "latest", "least", "less", "let", "lets", "like",
    "likely", "made", "make", "makes", "making", "many", "may", "member", "members",
    "men", "might", "more", "most", "mostly", "much", "must", "myself", "name", "necessary",
    "need", "needed", "needing", "needs", "never", "new", "newer", "newest", "next",
    "nobody", "non", "noone", "not", "nothing", "now", "nowhere", "number", "numbers",
    "off", "often", "old", "older", "oldest", "once", "one", "only", "open", "opened",
    "opening", "opens", "order", "ordered", "ordering", "orders", "other", "others",
    "our", "out", "over", "part", "parted", "parting", "parts", "per", "place", "places",
    "point", "pointed", "pointing", "points", "possible", "present", "presented",
    "presenting", "presents", "problem", "problems", "put", "puts", "quite", "rather",
    "really", "right", "room", "rooms", "said", "same", "saw", "say", "says", "second",
    "seconds", "see", "seem", "seemed", "seeming", "seems", "sees", "several", "shall",
    "she", "should", "side", "sides", "since", "small", "smaller", "smallest", "some",
    "somebody", "someone", "something", "somewhere", "state", "states", "still", "such",
    "sure", "take", "taken", "than", "that", "the", "their", "them", "then", "there",
    "therefore", "these", "they", "thing", "things", "think", "thinks", "this", "those",
    "though", "thought", "thoughts", "three", "through", "thus", "today", "together",
    "too", "took", "toward", "turn", "turned", "turning", "turns", "two", "under",
    "until", "upon", "use", "used", "uses", "very", "want", "wanted", "wanting", "wants",
    "was", "way", "ways", "well", "wells", "went", "were", "what", "when", "where",
    "whether", "which", "while", "who", "whole", "whose", "why", "will", "with", "within",
    "without", "work", "worked", "working", "works", "would", "year", "years", "yet",
    "you", "young", "younger", "youngest", "your", "yours"
}


def clear_screen() -> None:
    """Clear terminal screen across POSIX and NT environments."""
    os.system("cls" if os.name == "nt" else "clear")


def print_banner(silent: bool = False) -> None:
    """
    Render structured application header.

    Args:
        silent: If True, suppresses all banner output for pipeline integration.
    """
    if silent:
        return

    banner_text = (
        "========================================================================\n"
        "Destroyer Wordlist Generator - Targeted Security Profiling Utility\n"
        "========================================================================"
    )
    details = (
        "Modules: PCFG Grammar | Passphrase Engine | OSINT Harvester | GPU Rules\n"
        "Standards: NIST SP 800-63B Passphrase Specifications (8-64 chars)"
    )

    if RICH_AVAILABLE:
        p = Panel(
            f"[bold cyan]{banner_text}[/bold cyan]\n[dim white]{details}[/dim white]",
            border_style="blue",
            title="[bold green]Destroyer[/bold green]",
            subtitle="[dim]Security Assessment Utility[/dim]"
        )
        console.print(p)
    else:
        print(f"{C_CYAN}{banner_text}{C_RESET}")
        print(f"{details}\n")


# ==============================================================================
# HTML Harvester (OSINT Web Scraper)
# ==============================================================================

class HTMLTextExtractor(html.parser.HTMLParser):
    """
    Stream parser for extracting text tokens from HTML documents.
    Excludes non-content tags (script, style, noscript, svg, head).
    """

    def __init__(self) -> None:
        super().__init__()
        self.words: List[str] = []
        self._ignored_depth: int = 0
        self._ignore_tags: Set[str] = {"script", "style", "noscript", "svg", "path", "head"}

    def handle_starttag(self, tag: str, attrs: List[tuple[str, Optional[str]]]) -> None:
        if tag.lower() in self._ignore_tags:
            self._ignored_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in self._ignore_tags and self._ignored_depth > 0:
            self._ignored_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._ignored_depth == 0:
            matches = re.findall(r"[a-zA-Z]{4,25}", data)
            self.words.extend(matches)


def scrape_url_keywords(url: str, max_words: int = 50, timeout: int = 10) -> List[str]:
    """
    Harvest distinct high-frequency keywords from an HTTP/HTTPS endpoint.

    Args:
        url: Target web address to crawl.
        max_words: Maximum number of ranked keyword tokens to return.
        timeout: Network socket timeout in seconds.

    Returns:
        List of unique lowercased keyword tokens sorted by frequency.
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    headers = {
        "User-Agent": CONFIG.get("global", {}).get(
            "user_agent",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        )
    }

    req = urllib.request.Request(url, headers=headers)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    print(f"[*] Crawling endpoint: {url}")
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as response:
            content_type = response.headers.get("Content-Type", "")
            if "text/html" not in content_type and "application/xhtml" not in content_type:
                print(f"[-] Non-HTML MIME type ({content_type}), skipping extraction.")
                return []

            charset = "utf-8"
            if "charset=" in content_type.lower():
                charset = content_type.lower().split("charset=")[-1].split(";")[0].strip()

            raw_html = response.read().decode(charset, errors="ignore")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as err:
        print(f"[-] Network retrieval failed for {url}: {err}")
        return []

    parser = HTMLTextExtractor()
    parser.feed(raw_html)

    filtered_tokens = [
        token.lower() for token in parser.words
        if token.lower() not in STOP_WORDS and len(token) >= 4
    ]
    frequency_map = collections.Counter(filtered_tokens)
    ranked_keywords = [token for token, _ in frequency_map.most_common(max_words)]

    print(f"[+] Extracted {len(ranked_keywords)} distinct keyword tokens from {url}")
    return ranked_keywords


# ==============================================================================
# Configuration Parser
# ==============================================================================

def read_configuration(filename: Optional[str] = None) -> bool:
    """
    Load configuration parameters from an INI file into the CONFIG store.
    Uses interpolation=None to preserve punctuation characters without escaping.

    Args:
        filename: Path to the INI configuration file.

    Returns:
        True upon successful configuration population.
    """
    global CONFIG

    default_years = [str(y) for y in range(1950, 2031)]
    default_short_years = ["24", "25", "26", "27", "28", "29", "30", "95", "96", "97", "98", "99", "00", "01", "02", "03", "04", "05", "10", "15", "20", "21", "22", "23"]
    default_seasons = ["Spring", "Summer", "Autumn", "Fall", "Winter"]
    default_quarters = ["Q1", "Q2", "Q3", "Q4", "H1", "H2", "FY24", "FY25", "FY26", "FY27", "FY28"]
    default_months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    default_short_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    default_walks = ["123456", "12345678", "qweasd", "asdfgh", "zaq12wsx", "!@#$", "!@#$%^"]
    default_chars = ["!", "@", "#", "$", "%", "&", "*", "-", "_", "=", "+", "?", "~"]
    default_separators = ["-", "_", ".", "@", "#", "$", "!"]
    default_leet = {
        "a": "4", "i": "1", "e": "3", "t": "7", "o": "0", "s": "5", "g": "9", "z": "2", "b": "8"
    }

    config = configparser.ConfigParser(interpolation=None)
    if filename and os.path.isfile(filename):
        config.read(filename, encoding="utf-8")

    # [years]
    years_val = config.get("years", "years", fallback=",".join(default_years))
    years_list = [y.strip() for y in years_val.replace(".", ",").split(",") if y.strip()]

    short_years_val = config.get("years", "short_years", fallback=",".join(default_short_years))
    short_years_list = [sy.strip() for sy in short_years_val.split(",") if sy.strip()]

    # [corporate_cycles] with backward compatibility for [corporate_seasons]
    cycle_section = "corporate_cycles" if config.has_section("corporate_cycles") else "corporate_seasons"

    seasons_val = config.get(cycle_section, "seasons", fallback=",".join(default_seasons))
    seasons_list = [s.strip() for s in seasons_val.split(",") if s.strip()]

    quarters_val = config.get(cycle_section, "quarters", fallback=",".join(default_quarters))
    quarters_list = [q.strip() for q in quarters_val.split(",") if q.strip()]

    months_val = config.get(cycle_section, "months", fallback=",".join(default_months))
    months_list = [m.strip() for m in months_val.split(",") if m.strip()]

    short_months_val = config.get(cycle_section, "short_months", fallback=",".join(default_short_months))
    short_months_list = [sm.strip() for sm in short_months_val.split(",") if sm.strip()]

    # [keyboard_walks]
    walks_val = config.get("keyboard_walks", "walks", fallback=",".join(default_walks))
    walks_list = [w.strip() for w in walks_val.split(",") if w.strip()]

    # [specialchars]
    chars_val = config.get("specialchars", "chars", fallback=",".join(default_chars))
    chars_list = [c.strip() for c in chars_val.split(",") if c.strip()]

    # [separators]
    separators_val = config.get("separators", "separators", fallback=",".join(default_separators))
    separators_list = [sep.strip() for sep in separators_val.split(",") if sep.strip()]

    # [nums]
    num_from = config.getint("nums", "from", fallback=0)
    num_to = config.getint("nums", "to", fallback=100)

    # [shaping] with fallback to legacy [nums]
    wcfrom = config.getint("shaping", "wcfrom", fallback=config.getint("nums", "wcfrom", fallback=8))
    wcto = config.getint("shaping", "wcto", fallback=config.getint("nums", "wcto", fallback=64))
    threshold = config.getint("nums", "threshold", fallback=500)

    # [nist]
    min_passphrase_len = config.getint("nist", "min_passphrase_length", fallback=15)
    max_passphrase_len = config.getint("nist", "max_passphrase_length", fallback=64)

    # [scraper]
    user_agent = config.get("scraper", "user_agent", fallback="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    max_words = config.getint("scraper", "max_words", fallback=50)

    leet_dict: Dict[str, str] = {}
    if config.has_section("leet"):
        for key, val in config.items("leet"):
            leet_dict[key.lower()] = val
    else:
        leet_dict = default_leet

    CONFIG["global"] = {
        "years": years_list,
        "short_years": short_years_list,
        "seasons": seasons_list,
        "quarters": quarters_list,
        "months": months_list,
        "short_months": short_months_list,
        "walks": walks_list,
        "chars": chars_list,
        "separators": separators_list,
        "numfrom": num_from,
        "numto": num_to,
        "wcfrom": wcfrom,
        "wcto": wcto,
        "threshold": threshold,
        "min_passphrase_length": min_passphrase_len,
        "max_passphrase_length": max_passphrase_len,
        "user_agent": user_agent,
        "max_words": max_words,
    }
    CONFIG["LEET"] = leet_dict
    return True


# ==============================================================================
# Mutation and Entropy Utilities
# ==============================================================================

def apply_leet_conversion(input_string: str, mode: str = "standard") -> str:
    """
    Apply character substitution mapping to input string.

    Args:
        input_string: Source plaintext token.
        mode:
          - 'light': Replaces only highest-frequency substitutions (e->3, a->@, o->0, i->1, s->$).
          - 'standard': Performs full mapping defined in CONFIG['LEET'].

    Returns:
        Substituted string candidate.
    """
    if mode == "light":
        light_map = {"e": "3", "a": "@", "o": "0", "i": "1", "s": "$"}
        chars = list(input_string)
        for idx, char in enumerate(chars):
            lower_char = char.lower()
            if lower_char in light_map:
                chars[idx] = light_map[lower_char]
        return "".join(chars)

    result = input_string
    leet_map = CONFIG.get("LEET", {
        "a": "4", "i": "1", "e": "3", "t": "7", "o": "0", "s": "5", "g": "9", "z": "2", "b": "8"
    })
    for letter, replacement in leet_map.items():
        result = result.replace(letter, replacement).replace(letter.upper(), replacement)
    return result


def calculate_entropy(password: str) -> float:
    """
    Calculate theoretical keyspace entropy in bits.

    Formula:
        H = L * log2(|R|)
    where:
        L  = Character length of candidate string.
        |R| = Size of character pool based on detected character classes
              (lowercase=26, uppercase=26, digits=10, symbols=33).

    Args:
        password: Candidate password string.

    Returns:
        Entropy value in bits.
    """
    if not password:
        return 0.0

    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(not c.isalnum() for c in password)

    charset_cardinality = 0
    if has_lower:
        charset_cardinality += 26
    if has_upper:
        charset_cardinality += 26
    if has_digit:
        charset_cardinality += 10
    if has_symbol:
        charset_cardinality += 33

    charset_cardinality = max(charset_cardinality, 2)
    return len(password) * math.log2(charset_cardinality)


def extract_date_components(date_str: str) -> Dict[str, str]:
    """
    Parse calendar date representations into constituent numeric substrings.
    Supports DDMMYYYY, YYYYMMDD, delimited dates (DD-MM-YYYY, YYYY-MM-DD),
    and 4-digit year-only inputs.

    Args:
        date_str: Raw date string.

    Returns:
        Dictionary mapping component keys ('yyyy', 'yy', 'dd', 'mm', etc.) to numeric strings.
    """
    clean_date = re.sub(r"[^\d]", "", date_str.strip())
    components: Dict[str, str] = {}

    if len(clean_date) == 8:
        # Evaluate whether leading 4 digits represent a calendar year
        if 1900 < int(clean_date[:4]) < 2035:
            yyyy = clean_date[:4]
            mm = clean_date[4:6]
            dd = clean_date[6:8]
        else:
            dd = clean_date[:2]
            mm = clean_date[2:4]
            yyyy = clean_date[4:]

        yy = yyyy[-2:]
        components["yyyy"] = yyyy
        components["yy"] = yy
        components["dd"] = dd
        components["mm"] = mm
        components["ddmm"] = dd + mm
        components["mmdd"] = mm + dd
        components["ddmmyyyy"] = dd + mm + yyyy
        components["yyyymmdd"] = yyyy + mm + dd
        components["ddmmyy"] = dd + mm + yy
    elif len(clean_date) == 4:
        components["yyyy"] = clean_date
        components["yy"] = clean_date[-2:]

    return components


# ==============================================================================
# Target Profile Model
# ==============================================================================

class TargetProfile:
    """
    Structured data model representing reconnaissance attributes gathered
    for a target entity or organization.
    """

    def __init__(self) -> None:
        self.name: str = ""
        self.surname: str = ""
        self.nick: str = ""
        self.handles: List[str] = []
        self.email: str = ""
        self.birthdate: str = ""
        self.birth_components: Dict[str, str] = {}

        # Associates and relations
        self.partner_name: str = ""
        self.partner_nick: str = ""
        self.partner_birthdate: str = ""
        self.partner_birth_components: Dict[str, str] = {}

        self.guardian_name: str = ""
        self.guardian_nick: str = ""
        self.guardian_birthdate: str = ""
        self.guardian_birth_components: Dict[str, str] = {}

        self.children_names: List[str] = []
        self.pet_names: List[str] = []

        # Organizational and corporate parameters
        self.company: str = ""
        self.company_acronym: str = ""
        self.department: str = ""
        self.domain: str = ""
        self.project_names: List[str] = []
        self.target_url: str = ""

        # Lifestyle and contextual keywords
        self.mobile: str = ""
        self.city: str = ""
        self.sports_team: str = ""
        self.keywords: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        """Serialize profile parameters to JSON-compatible dictionary."""
        return {
            "name": self.name,
            "surname": self.surname,
            "nick": self.nick,
            "handles": self.handles,
            "email": self.email,
            "birthdate": self.birthdate,
            "partner_name": self.partner_name,
            "partner_nick": self.partner_nick,
            "partner_birthdate": self.partner_birthdate,
            "guardian_name": self.guardian_name,
            "guardian_nick": self.guardian_nick,
            "guardian_birthdate": self.guardian_birthdate,
            "children_names": self.children_names,
            "pet_names": self.pet_names,
            "company": self.company,
            "company_acronym": self.company_acronym,
            "department": self.department,
            "domain": self.domain,
            "project_names": self.project_names,
            "target_url": self.target_url,
            "mobile": self.mobile,
            "city": self.city,
            "sports_team": self.sports_team,
            "keywords": self.keywords,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TargetProfile:
        """Instantiate and populate a TargetProfile from dictionary data."""
        p = cls()
        p.name = data.get("name", "").strip().lower()
        p.surname = data.get("surname", "").strip().lower()
        p.nick = data.get("nick", "").strip().lower()
        p.handles = [h.strip().lower() for h in data.get("handles", []) if h.strip()]
        p.email = data.get("email", "").strip().lower()
        p.birthdate = data.get("birthdate", "").strip()
        p.birth_components = extract_date_components(p.birthdate)

        p.partner_name = data.get("partner_name", "").strip().lower()
        p.partner_nick = data.get("partner_nick", "").strip().lower()
        p.partner_birthdate = data.get("partner_birthdate", "").strip()
        p.partner_birth_components = extract_date_components(p.partner_birthdate)

        p.guardian_name = data.get("guardian_name", "").strip().lower()
        p.guardian_nick = data.get("guardian_nick", "").strip().lower()
        p.guardian_birthdate = data.get("guardian_birthdate", "").strip()
        p.guardian_birth_components = extract_date_components(p.guardian_birthdate)

        p.children_names = [c.strip().lower() for c in data.get("children_names", []) if c.strip()]
        p.pet_names = [pet.strip().lower() for pet in data.get("pet_names", []) if pet.strip()]

        p.company = data.get("company", "").strip().lower()
        p.company_acronym = data.get("company_acronym", "").strip().lower()
        p.department = data.get("department", "").strip().lower()
        p.domain = data.get("domain", "").strip().lower()
        p.project_names = [pr.strip().lower() for pr in data.get("project_names", []) if pr.strip()]
        p.target_url = data.get("target_url", "").strip()

        p.mobile = re.sub(r"[^\d]", "", data.get("mobile", ""))
        p.city = data.get("city", "").strip().lower()
        p.sports_team = data.get("sports_team", "").strip().lower()
        p.keywords = [kw.strip().lower() for kw in data.get("keywords", []) if kw.strip()]
        return p


# ==============================================================================
# Combinatorial Generation Engine
# ==============================================================================

class DestroyerGenerator:
    """
    Combinatorial candidate generation engine.
    Applies Probabilistic Context-Free Grammar (PCFG) production templates,
    temporal token injection, selective leetspeak transforms, and streaming deduplication.
    """

    def __init__(
        self,
        profile: TargetProfile,
        mode: str = "standard",
        min_len: int = 8,
        max_len: int = 64,
        leet_mode: str = "light",
        include_corporate: bool = True,
        nist_mode: bool = False,
    ) -> None:
        """
        Initialize the generator with target parameters and constraints.

        Args:
            profile: TargetProfile instance containing reconnaissance tokens.
            mode: Candidate generation depth ('fast', 'standard', 'deep', 'passphrase').
            min_len: Minimum acceptable candidate string length.
            max_len: Maximum acceptable candidate string length.
            leet_mode: Mutation strategy ('off', 'light', 'standard').
            include_corporate: Whether to generate organizational and directory rollover candidates.
            nist_mode: Enforce NIST SP 800-63B minimum length bound of 15 characters.
        """
        self.profile = profile
        self.mode = mode.lower()
        self.min_len = 15 if nist_mode else max(1, min_len)
        self.max_len = max(self.min_len, max_len)
        self.leet_mode = leet_mode.lower()
        self.include_corporate = include_corporate
        self.nist_mode = nist_mode

        if "global" not in CONFIG:
            read_configuration()

        self.cfg = CONFIG["global"]

        self.primary_tokens: List[str] = self._extract_primary_tokens()
        self.secondary_tokens: List[str] = self._extract_secondary_tokens()
        self.date_tokens: List[str] = self._extract_date_tokens()

    def _extract_primary_tokens(self) -> List[str]:
        """Extract primary target entity identifiers and user tokens."""
        p = self.profile
        tokens: Set[str] = set()

        for val in [p.name, p.surname, p.nick]:
            if val:
                tokens.add(val)

        if p.name and p.surname:
            tokens.add(p.name + p.surname)
            tokens.add(p.name[0] + p.surname)
            tokens.add(p.name + "." + p.surname)
            tokens.add(p.name + "_" + p.surname)

        for handle in p.handles:
            tokens.add(handle)

        if p.email and "@" in p.email:
            email_local_part = p.email.split("@")[0]
            tokens.add(email_local_part)

        for kw in p.keywords:
            tokens.add(kw)

        return [t for t in tokens if len(t) >= 2]

    def _extract_secondary_tokens(self) -> List[str]:
        """Extract associate identifiers and organizational tokens."""
        p = self.profile
        tokens: Set[str] = set()

        for val in [p.partner_name, p.partner_nick, p.guardian_name, p.guardian_nick, p.city, p.sports_team]:
            if val:
                tokens.add(val)

        for child in p.children_names:
            tokens.add(child)
        for pet in p.pet_names:
            tokens.add(pet)

        if p.company:
            tokens.add(p.company)
        if p.company_acronym:
            tokens.add(p.company_acronym)
        if p.department:
            tokens.add(p.department)
        if p.domain:
            domain_label = p.domain.split(".")[0]
            tokens.add(domain_label)
        for project in p.project_names:
            tokens.add(project)

        return [t for t in tokens if len(t) >= 2]

    def _extract_date_tokens(self) -> List[str]:
        """Extract calendar substrings and phone suffix tokens."""
        tokens: Set[str] = set()
        p = self.profile

        for date_dict in [p.birth_components, p.partner_birth_components, p.guardian_birth_components]:
            for _, val in date_dict.items():
                if val:
                    tokens.add(val)

        if len(p.mobile) >= 4:
            tokens.add(p.mobile[-4:])
        if len(p.mobile) >= 6:
            tokens.add(p.mobile[-6:])
        if len(p.mobile) >= 10:
            tokens.add(p.mobile[-10:])

        return list(tokens)

    def _casing_variants(self, word: str) -> List[str]:
        """Generate capitalization permutations (Title, lowercase, UPPERCASE)."""
        if not word:
            return []
        variants = [word.capitalize(), word.lower()]
        if self.mode in ("standard", "deep"):
            variants.append(word.upper())
        return list(dict.fromkeys(variants))

    def generate_candidates(self) -> Generator[str, None, None]:
        """
        Streaming generator executing PCFG production templates.
        Yields candidate strings sequentially without intermediate list buffering.
        """
        priority_years = ["2027", "2026", "2025", "2024", "2028", "2029", "2030", "2023", "2022", "2020"]
        if self.mode == "deep":
            all_years = list(dict.fromkeys(priority_years + self.cfg["years"]))
        else:
            all_years = list(dict.fromkeys(priority_years + self.cfg["years"][:30]))

        short_years = self.cfg.get("short_years", ["27", "26", "25", "24", "28", "29", "30"])
        special_chars = self.cfg.get("chars", ["!", "@", "#", "$", "%", "*", "_"])
        separators = self.cfg.get("separators", ["-", "_", ".", "@", "#", "$", "!"])
        seasons = self.cfg.get("seasons", ["Spring", "Summer", "Autumn", "Fall", "Winter"])
        quarters = self.cfg.get("quarters", ["Q1", "Q2", "Q3", "Q4", "FY26", "FY27", "FY28"])
        months = self.cfg.get("months", ["January", "February", "March", "October", "November", "December"])
        short_months = self.cfg.get("short_months", ["Jan", "Feb", "Mar", "Oct", "Nov", "Dec"])
        walks = self.cfg.get("walks", ["123456", "12345678", "qweasd", "!@#$%^"])

        # -------------------------------------------------------------
        # PCFG Template: Multi-token Passphrases (NIST SP 800-63B)
        # Production: S -> Token1 [Sep] Token2 [Sep] Year [Sym]
        # -------------------------------------------------------------
        all_pool = list(dict.fromkeys(self.primary_tokens + self.secondary_tokens))
        if self.nist_mode or self.mode in ("passphrase", "deep", "standard"):
            for w1 in all_pool:
                for w2 in all_pool:
                    if w1.lower() == w2.lower():
                        continue
                    w1_c = w1.capitalize()
                    w2_c = w2.capitalize()
                    for sep in separators[:6]:
                        for yr in ["2027", "2026", "2025", "2028"]:
                            for sym in ["!", "#", "$", "@", ""]:
                                yield f"{w1_c}{sep}{w2_c}{sep}{yr}{sym}"
                                yield f"{w1_c}{sep}{yr}{sep}{w2_c}{sym}"

            # 3-token passphrase synthesis in deep / passphrase modes
            if self.mode in ("passphrase", "deep") and len(all_pool) >= 3:
                for w1 in all_pool[:6]:
                    for w2 in all_pool[:6]:
                        if w1.lower() == w2.lower():
                            continue
                        for w3 in all_pool[:6]:
                            if w3.lower() in (w1.lower(), w2.lower()):
                                continue
                            w1_c, w2_c, w3_c = w1.capitalize(), w2.capitalize(), w3.capitalize()
                            for sep in ["-", "_", " "]:
                                yield f"{w1_c}{sep}{w2_c}{sep}{w3_c}"
                                yield f"{w1_c}{sep}{w2_c}{sep}{w3_c}2027!"

        if self.mode == "passphrase":
            return

        # -------------------------------------------------------------
        # PCFG Template: Organizational & Directory Rotation Patterns
        # Production: S -> CorpToken [Year] [Special]
        #             S -> Season/Month [Year] [Special]
        # -------------------------------------------------------------
        if self.include_corporate:
            corp_words = [self.profile.company, self.profile.company_acronym, "Welcome", "Admin", "Password"]
            corp_words = [w for w in corp_words if w]

            for cw in corp_words:
                cw_cap = cw.capitalize()
                for yr in ["2027", "2026", "2025", "2028", "2024"]:
                    for sym in special_chars[:8]:
                        yield f"{cw_cap}{yr}{sym}"
                        yield f"{cw_cap}@{yr}"
                        yield f"{cw_cap}#{yr}"
                        yield f"{cw_cap}!{yr}"
                        yield f"{cw_cap}{sym}{yr}"
                        yield f"{sym}{cw_cap}{yr}"

            for season in seasons:
                for yr in ["2027", "2026", "2025", "2028"]:
                    for sym in ["!", "@", "#", "$", "*"]:
                        yield f"{season}{yr}{sym}"
                        yield f"{season}{sym}{yr}"
                        yield f"{season}{yr}"
                        yield f"{season.lower()}{yr}{sym}"

            for month in (months + short_months):
                for yr in ["2027", "2026", "2025", "2028"]:
                    for sym in ["!", "@", "#", "$"]:
                        yield f"{month}{yr}{sym}"
                        yield f"{month}@{yr}"
                        yield f"{month}#{yr}"

            for qtr in quarters:
                for yr in ["2027", "2026", "2025", "2028", "27", "26"]:
                    for sym in ["!", "@", "#", "$"]:
                        yield f"{qtr}{yr}{sym}"
                        yield f"{qtr}@{yr}"

        # -------------------------------------------------------------
        # PCFG Template: Primary Entity Tokens + Temporal / Sequence / Walks
        # Production: S -> BaseWord [Year/Seq/Walk] [Special]
        # -------------------------------------------------------------
        for token in self.primary_tokens:
            for variant in self._casing_variants(token):
                for yr in all_years:
                    yield f"{variant}{yr}"
                    for sym in special_chars[:8]:
                        yield f"{variant}{yr}{sym}"
                        yield f"{variant}{sym}{yr}"
                        yield f"{sym}{variant}{yr}"

                for sy in short_years:
                    yield f"{variant}{sy}"
                    for sym in special_chars[:6]:
                        yield f"{variant}{sy}{sym}"
                        yield f"{variant}@{sy}"

                for seq in ["123", "1234", "12345", "123456", "01", "007", "777", "999"]:
                    yield f"{variant}{seq}"
                    for sym in ["!", "@", "#", "$"]:
                        yield f"{variant}{seq}{sym}"
                        yield f"{variant}{sym}{seq}"

                for walk in walks:
                    yield f"{variant}{walk}"
                    yield f"{walk}{variant}"

        # -------------------------------------------------------------
        # PCFG Template: Entity Tokens + Date Substrings
        # Production: S -> BaseWord [DateComponent] [Special]
        # -------------------------------------------------------------
        for token in self.primary_tokens:
            for variant in self._casing_variants(token):
                for dt in self.date_tokens:
                    yield f"{variant}{dt}"
                    yield f"{dt}{variant}"
                    for sym in ["!", "@", "#", "_"]:
                        yield f"{variant}{sym}{dt}"
                        yield f"{variant}{dt}{sym}"

        # -------------------------------------------------------------
        # PCFG Template: Entity + Associate Token Coupling
        # Production: S -> PrimaryWord [Delimiter] SecondaryWord [Year] [Sym]
        # -------------------------------------------------------------
        for p_tok in self.primary_tokens:
            p_cap = p_tok.capitalize()
            for s_tok in self.secondary_tokens:
                s_cap = s_tok.capitalize()
                for sep in ["", "_", ".", "-", "@", "&"]:
                    base_combo = f"{p_cap}{sep}{s_cap}"
                    yield base_combo
                    for yr in ["2027", "2026", "2025", "2024", "123"]:
                        yield f"{base_combo}{yr}"
                        for sym in ["!", "@", "#"]:
                            yield f"{base_combo}{yr}{sym}"

        # -------------------------------------------------------------
        # PCFG Template: Leetspeak Substitutions
        # Production: S -> LeetTransform(Word) [Year/Seq] [Special]
        # -------------------------------------------------------------
        if self.leet_mode != "off":
            leet_base_list = self.primary_tokens.copy()
            if self.mode in ("standard", "deep"):
                leet_base_list += self.secondary_tokens[:5]

            for tok in leet_base_list:
                leet_light = apply_leet_conversion(tok, mode="light")
                leet_full = apply_leet_conversion(tok, mode="standard") if self.leet_mode == "standard" else leet_light

                for mutated in {leet_light, leet_full}:
                    if mutated == tok:
                        continue
                    yield mutated
                    for yr in ["2027", "2026", "2025", "123", "01"]:
                        for sym in ["!", "@", "#", "$", ""]:
                            yield f"{mutated}{yr}{sym}"
                            yield f"{mutated.capitalize()}{yr}{sym}"

        # -------------------------------------------------------------
        # Deep Mode: Exhaustive Suffix Padding and Token Reversals
        # -------------------------------------------------------------
        if self.mode == "deep":
            num_start = self.cfg.get("numfrom", 0)
            num_stop = min(self.cfg.get("numto", 100), 200)
            for token in self.primary_tokens:
                token_cap = token.capitalize()
                for num in range(num_start, num_stop):
                    yield f"{token_cap}{num}"
                    yield f"{token_cap}{num:02d}"
                    yield f"{token_cap}@{num}"

                reversed_token = token[::-1]
                yield reversed_token
                yield f"{reversed_token}2027!"

    def generate_and_save(self, output_file: str) -> Dict[str, Any]:
        """
        Execute streaming pipeline, filter length boundaries, deduplicate,
        measure keyspace entropy, and write output atomically.

        Args:
            output_file: Destination filepath for compiled dictionary.

        Returns:
            Dictionary containing metrics: total words, throughput, file size,
            average entropy, and elapsed execution time.
        """
        start_time = time.time()
        seen: Set[str] = set()
        total_count = 0
        nist_compliant_count = 0
        total_entropy = 0.0

        output_dir = os.path.dirname(os.path.abspath(output_file))
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        with open(output_file, "w", encoding="utf-8", buffering=65536) as fh:
            for candidate in self.generate_candidates():
                cand_len = len(candidate)
                if cand_len < self.min_len or cand_len > self.max_len:
                    continue

                if candidate not in seen:
                    seen.add(candidate)
                    fh.write(candidate + "\n")
                    total_count += 1
                    total_entropy += calculate_entropy(candidate)

                    if cand_len >= 15:
                        nist_compliant_count += 1

                    # Bound memory usage by clearing the cache if tracking exceeds threshold
                    if len(seen) > 1500000:
                        seen.clear()

        elapsed = time.time() - start_time
        file_size_kb = os.path.getsize(output_file) / 1024.0
        avg_entropy = (total_entropy / total_count) if total_count > 0 else 0.0

        return {
            "total_words": total_count,
            "nist_compliant": nist_compliant_count,
            "avg_entropy": avg_entropy,
            "elapsed_seconds": elapsed,
            "speed_wps": (total_count / elapsed) if elapsed > 0 else float(total_count),
            "file_size_kb": file_size_kb,
            "output_path": os.path.abspath(output_file),
        }

    def export_hashcat_rules(self, rule_file_path: str) -> None:
        """
        Generate a targeted Hashcat / John the Ripper rule file (.rule).

        Args:
            rule_file_path: Destination path for rule definitions.
        """
        rules = [
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
            # Contemporary year appendages
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

        output_dir = os.path.dirname(os.path.abspath(rule_file_path))
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        with open(rule_file_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(rules) + "\n")

    def export_hashcat_masks(self, mask_file_path: str) -> None:
        """
        Generate a targeted Hashcat mask configuration file (.hcmask).

        Args:
            mask_file_path: Destination path for mask configurations.
        """
        masks = [
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

        output_dir = os.path.dirname(os.path.abspath(mask_file_path))
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        with open(mask_file_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(masks) + "\n")


# ==============================================================================
# Terminal Interaction & Reporting
# ==============================================================================

def prompt_interactive() -> TargetProfile:
    """
    Execute terminal profiling questionnaire to populate TargetProfile parameters.

    Returns:
        Populated TargetProfile instance.
    """
    if RICH_AVAILABLE:
        console.print("[bold cyan][*] Initializing Reconnaissance Profiling Questionnaire[/bold cyan]")
        console.print("[dim white]Press Enter on optional fields to skip.[/dim white]\n")
    else:
        print("[*] Initializing Reconnaissance Profiling Questionnaire")
        print("Press Enter on optional fields to skip.\n")

    data: Dict[str, Any] = {}

    # Section 1: Entity Identification
    if RICH_AVAILABLE:
        console.print("[bold yellow]1. Primary Target Identification[/bold yellow]")
    else:
        print("1. Primary Target Identification")

    name = input("> First Name: ").strip().lower()
    while not name:
        print("[-] Error: Primary name is required to establish target context.")
        name = input("> First Name: ").strip().lower()

    data["name"] = name
    data["surname"] = input("> Surname: ").strip().lower()
    data["nick"] = input("> Nickname / Alias: ").strip().lower()

    handles_in = input("> Known Handles / Usernames (comma-separated): ").strip()
    data["handles"] = [h.strip().lower() for h in handles_in.split(",") if h.strip()]

    data["email"] = input("> Email Address: ").strip().lower()
    data["birthdate"] = input("> Birthdate (DDMMYYYY / YYYY-MM-DD / YYYY): ").strip()
    data["mobile"] = input("> Telephone Number: ").strip()

    # Section 2: Associated Entities
    print()
    if RICH_AVAILABLE:
        console.print("[bold yellow]2. Associates, Relations & Identifiers[/bold yellow]")
    else:
        print("2. Associates, Relations & Identifiers")

    data["partner_name"] = input("> Partner / Spouse Name: ").strip().lower()
    data["partner_nick"] = input("> Partner Alias: ").strip().lower()
    data["partner_birthdate"] = input("> Partner Birthdate: ").strip()

    children_in = input("> Children Names (comma-separated): ").strip()
    data["children_names"] = [c.strip().lower() for c in children_in.split(",") if c.strip()]

    pets_in = input("> Pet Names (comma-separated): ").strip()
    data["pet_names"] = [p.strip().lower() for p in pets_in.split(",") if p.strip()]

    # Section 3: Organizational Context
    print()
    if RICH_AVAILABLE:
        console.print("[bold yellow]3. Organizational & Enterprise Parameters[/bold yellow]")
    else:
        print("3. Organizational & Enterprise Parameters")

    data["company"] = input("> Organization / Employer: ").strip().lower()
    data["company_acronym"] = input("> Organization Acronym: ").strip().lower()
    data["department"] = input("> Department (e.g. IT, DevOps, Finance): ").strip().lower()
    data["domain"] = input("> Enterprise Domain (e.g. corp.internal): ").strip().lower()

    projects_in = input("> Internal Projects / Codename Tokens (comma-separated): ").strip()
    data["project_names"] = [pr.strip().lower() for pr in projects_in.split(",") if pr.strip()]

    target_url = input("> Organizational Web Endpoint to Crawl (optional): ").strip()
    data["target_url"] = target_url

    # Section 4: Geographical and Contextual Keywords
    print()
    if RICH_AVAILABLE:
        console.print("[bold yellow]4. Geographical & Custom Keywords[/bold yellow]")
    else:
        print("4. Geographical & Custom Keywords")

    data["city"] = input("> City / Primary Location: ").strip().lower()
    data["sports_team"] = input("> Affiliation / Sports Team: ").strip().lower()

    keywords_in = input("> Additional Keywords (comma-separated): ").strip()
    base_keywords = [kw.strip().lower() for kw in keywords_in.split(",") if kw.strip()]

    if target_url:
        scraped_tokens = scrape_url_keywords(target_url, max_words=50)
        base_keywords.extend(scraped_tokens)

    data["keywords"] = list(dict.fromkeys(base_keywords))
    return TargetProfile.from_dict(data)


def display_summary(stats: Dict[str, Any]) -> None:
    """
    Render compilation metrics and keyspace entropy statistics.

    Args:
        stats: Output dictionary from DestroyerGenerator.generate_and_save.
    """
    if RICH_AVAILABLE:
        table = Table(title="[bold green]Compilation Metrics[/bold green]", border_style="blue")
        table.add_column("Parameter", style="bold white")
        table.add_column("Measurement", style="bold yellow")

        table.add_row("Total Generated Candidates", f"{stats['total_words']:,}")
        table.add_row("NIST SP 800-63B Compliant (>= 15 chars)", f"{stats['nist_compliant']:,}")
        table.add_row("Mean Keyspace Entropy", f"{stats['avg_entropy']:.2f} bits")
        table.add_row("Execution Duration", f"{stats['elapsed_seconds']:.2f} s")
        table.add_row("Generation Rate", f"{stats['speed_wps']:,.0f} words/s")
        table.add_row("Output File Size", f"{stats['file_size_kb']:.2f} KB")
        table.add_row("Destination", f"{stats['output_path']}")
        console.print("\n", table, "\n")
    else:
        print("\n" + "=" * 64)
        print(" COMPILATION METRICS")
        print("=" * 64)
        print(f" Total Generated Candidates : {stats['total_words']:,}")
        print(f" NIST SP 800-63B (>= 15 ch) : {stats['nist_compliant']:,}")
        print(f" Mean Keyspace Entropy      : {stats['avg_entropy']:.2f} bits")
        print(f" Execution Duration         : {stats['elapsed_seconds']:.2f} s")
        print(f" Generation Rate            : {stats['speed_wps']:,.0f} words/s")
        print(f" Output File Size           : {stats['file_size_kb']:.2f} KB")
        print(f" Destination                : {stats['output_path']}")
        print("=" * 64 + "\n")


def generate_wordlist_from_profile(profile_dict: Dict[str, Any], output_file: str = "passwords.txt") -> List[str]:
    """
    API entry point for programmatic usage from external testing suites.

    Args:
        profile_dict: Dictionary conforming to TargetProfile schema.
        output_file: Target filepath for generated wordlist.

    Returns:
        List of generated candidate strings.
    """
    profile = TargetProfile.from_dict(profile_dict)
    generator = DestroyerGenerator(profile=profile, mode="standard", min_len=8, max_len=64)
    stats = generator.generate_and_save(output_file)
    display_summary(stats)

    with open(output_file, "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh]


# ==============================================================================
# CLI Entry Point
# ==============================================================================

def parse_arguments() -> argparse.Namespace:
    """Configure and parse command-line interface arguments."""
    parser = argparse.ArgumentParser(
        description="Destroyer Wordlist Generator - Targeted Security Profiling Utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python wordlist_generator.py -i
  python wordlist_generator.py -p profile.json -o wordlist.txt
  python wordlist_generator.py -p profile.json --url https://target.internal -o corp_wordlist.txt
  python wordlist_generator.py -p profile.json --mode deep --hashcat-rules custom.rule --hashcat-masks custom.hcmask
  python wordlist_generator.py -p profile.json --nist -o nist_passphrases.txt
        """
    )
    parser.add_argument("-i", "--interactive", action="store_true", help="Launch terminal questionnaire wizard")
    parser.add_argument("-p", "--profile", type=str, help="Load target profile from a JSON file")
    parser.add_argument("-u", "--url", type=str, help="Harvest keywords from an HTTP/HTTPS endpoint")
    parser.add_argument("-o", "--output", type=str, default="passwords.txt", help="Output file path (default: passwords.txt)")
    parser.add_argument("-m", "--mode", choices=["fast", "standard", "deep", "passphrase"], default="standard",
                        help="Combinatorial depth mode (default: standard)")
    parser.add_argument("--min-len", type=int, default=8, help="Minimum candidate length filter (default: 8)")
    parser.add_argument("--max-len", type=int, default=64, help="Maximum candidate length filter (default: 64)")
    parser.add_argument("--nist", action="store_true", help="Enforce NIST SP 800-63B standard (minimum length: 15)")
    parser.add_argument("--leet", choices=["off", "light", "standard"], default="light",
                        help="Mutation depth: off, light (selective), or standard (default: light)")
    parser.add_argument("--no-corporate", action="store_true", help="Disable organizational directory patterns")
    parser.add_argument("--hashcat-rules", type=str, help="Export targeted Hashcat rule file (.rule)")
    parser.add_argument("--hashcat-masks", type=str, help="Export targeted Hashcat mask configuration (.hcmask)")
    parser.add_argument("--save-profile", type=str, help="Save questionnaire inputs to JSON for replayability")
    parser.add_argument("--no-banner", action="store_true", help="Suppress terminal header for pipe operations")
    parser.add_argument("--inspect", action="store_true", help="Print top 50 generated candidates upon completion")
    return parser.parse_args()


def main() -> None:
    """Execution coordinator."""
    args = parse_arguments()

    config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "destroyer.cfg")
    read_configuration(config_path)

    print_banner(silent=args.no_banner)

    target_profile: Optional[TargetProfile] = None

    if args.profile:
        if not os.path.isfile(args.profile):
            print(f"[-] Error: Profile file '{args.profile}' not found.")
            sys.exit(1)
        with open(args.profile, "r", encoding="utf-8") as fh:
            profile_data = json.load(fh)
            target_profile = TargetProfile.from_dict(profile_data)
            print(f"[+] Loaded target profile: {args.profile}")
    else:
        target_profile = prompt_interactive()

    # Optional URL crawling override
    if args.url:
        scraped_keywords = scrape_url_keywords(
            args.url,
            max_words=CONFIG["global"].get("max_words", 50)
        )
        target_profile.keywords = list(dict.fromkeys(target_profile.keywords + scraped_keywords))

    if args.save_profile:
        with open(args.save_profile, "w", encoding="utf-8") as fh:
            json.dump(target_profile.to_dict(), fh, indent=4)
        print(f"[+] Saved profile configuration: {args.save_profile}")

    generator = DestroyerGenerator(
        profile=target_profile,
        mode=args.mode,
        min_len=args.min_len,
        max_len=args.max_len,
        leet_mode=args.leet,
        include_corporate=not args.no_corporate,
        nist_mode=args.nist,
    )

    print(f"[*] Executing generation pipeline (Mode: {args.mode.upper()})...")

    stats = generator.generate_and_save(args.output)
    display_summary(stats)

    if args.hashcat_rules:
        generator.export_hashcat_rules(args.hashcat_rules)
        print(f"[+] Hashcat rule file written: {args.hashcat_rules}")

    if args.hashcat_masks:
        generator.export_hashcat_masks(args.hashcat_masks)
        print(f"[+] Hashcat mask file written: {args.hashcat_masks}")

    if args.inspect:
        print(f"[*] Head inspection (top 50 lines from {args.output}):")
        try:
            with open(args.output, "r", encoding="utf-8") as fh:
                for idx, line in enumerate(fh):
                    if idx >= 50:
                        break
                    print(f" {idx + 1:02d}: {line.strip()}")
        except OSError as err:
            print(f"[-] Read error during inspection: {err}")

    print("[+] Wordlist compilation completed.")


if __name__ == "__main__":
    main()
