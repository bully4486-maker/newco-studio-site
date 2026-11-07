"""Banned copy patterns for NEW masters. Automated gate only — not a creative/rights score."""

from __future__ import annotations

import re
from typing import Iterable

# Phrases that must not appear in new configs / captions / on-screen copy.
# Keep specific; do not ban the word "example".
BANNED_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("demo_site_fictional", re.compile(r"demo\s*site\s*[·.•\-–—]?\s*fictional", re.I)),
    ("fictional_business", re.compile(r"fictional\s+business", re.I)),
    ("founding_offer", re.compile(r"\bfounding\b", re.I)),
    ("first_3_clients", re.compile(r"first\s*3\s*clients|first\s*three\s*clients", re.I)),
    ("mtd_ready", re.compile(r"\bmtd[\s\-]?ready\b", re.I)),
    ("voiceover", re.compile(r"\bvoice[\s\-]?over\b|\bnarration\b|\bTTS\b|\btext[\s\-]?to[\s\-]?speech\b", re.I)),
    ("comedy", re.compile(r"\bcomedy\b|\bskit\b|\bsketch\b", re.I)),
    ("invented_testimonial", re.compile(
        r"\b(testimonial|\"[^\"]{8,}\")\b.*\b(loved|amazing|changed my business)\b"
        r"|\bstars?\s*out of\s*5\b|\b5/5\b",
        re.I,
    )),
    ("hearth_crumb_republish", re.compile(r"hearth\s*&\s*crumb|hearth\s+and\s+crumb", re.I)),
    ("fake_cafe_menu", re.compile(r"\bflat\s*white\b|\bbook a table\b", re.I)),
    # Cafe/restaurant-specific hooks mismatch general trade examples (e.g. electrician)
    ("cafe_specific_hook", re.compile(
        r"menu,\s*hours\s*&\s*booking|hours\s*&\s*booking,\s*one\s*page",
        re.I,
    )),
]

# Platform-only / non-cross-licence music claims are rejected separately in music.py.


def scan_text(text: str) -> list[str]:
    hits: list[str] = []
    if not text:
        return hits
    for name, pat in BANNED_PATTERNS:
        if pat.search(text):
            hits.append(name)
    return hits


def scan_many(parts: Iterable[str]) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for part in parts:
        for hit in scan_text(part or ""):
            if hit not in seen:
                seen.add(hit)
                found.append(hit)
    return found
