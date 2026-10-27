"""
HTTP Reconnaissance Harvester
=============================
Crawls organizational web endpoints and extracts high-frequency keyword tokens.
"""

from __future__ import annotations

import collections
import html.parser
import re
import ssl
from typing import List, Optional, Set, Tuple
import urllib.error
import urllib.request
from destroyer.osint.normalizer import STOP_WORDS


class HTMLTextExtractor(html.parser.HTMLParser):
    """HTML parser extracting text nodes while ignoring scripts and styling."""

    def __init__(self) -> None:
        super().__init__()
        self.words: List[str] = []
        self._depth: int = 0
        self._ignore: Set[str] = {"script", "style", "noscript", "svg", "path", "head"}

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if tag.lower() in self._ignore:
            self._depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in self._ignore and self._depth > 0:
            self._depth -= 1

    def handle_data(self, data: str) -> None:
        if self._depth == 0:
            tokens = re.findall(r"[a-zA-Z]{4,25}", data)
            self.words.extend(tokens)


def harvest_endpoint_keywords(
    url: str,
    max_words: int = 50,
    timeout: int = 10,
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
) -> List[str]:
    """
    Harvest ranked distinct keywords from an HTTP/HTTPS endpoint.

    Args:
        url: Target web address.
        max_words: Maximum number of ranked keyword tokens.
        timeout: Socket timeout in seconds.
        user_agent: User-Agent header value.

    Returns:
        List of ranked unique keyword strings.
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    headers = {"User-Agent": user_agent}
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
        print(f"[-] Harvester failed for {url}: {err}")
        return []

    parser = HTMLTextExtractor()
    parser.feed(raw_html)

    filtered = [
        w.lower() for w in parser.words
        if w.lower() not in STOP_WORDS and len(w) >= 4
    ]
    frequencies = collections.Counter(filtered)
    top_tokens = [token for token, _ in frequencies.most_common(max_words)]

    print(f"[+] Extracted {len(top_tokens)} distinct keyword tokens from {url}")
    return top_tokens
