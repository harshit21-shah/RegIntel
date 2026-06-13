"""Prompt-injection defenses for untrusted regulatory text."""

from __future__ import annotations

import re

INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.I),
    re.compile(r"disregard\s+(the\s+)?(system|above)", re.I),
    re.compile(r"you\s+are\s+now\s+", re.I),
    re.compile(r"<\/?system>", re.I),
]


def detect_injection(text: str) -> bool:
    return any(pattern.search(text) for pattern in INJECTION_PATTERNS)


def sanitize_untrusted_content(text: str, *, label: str = "source_document") -> str:
    cleaned = text.replace("<system>", "&lt;system&gt;").replace("</system>", "&lt;/system&gt;")
    return f"<{label}>\n{cleaned}\n</{label}>"


def wrap_for_agent(text: str, *, label: str = "source_document") -> str:
    if detect_injection(text):
        text = re.sub(r"(?i)ignore\s+(all\s+)?previous\s+instructions", "[filtered]", text)
    return sanitize_untrusted_content(text, label=label)
