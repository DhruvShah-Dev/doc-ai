"""Small, deterministic quality summary for extracted document text."""

from __future__ import annotations


def describe_text(text: str | None) -> dict[str, int | bool | float]:
    content = text or ""
    words = content.split()
    visible = [character for character in content if not character.isspace()]
    return {
        "characters": len(content),
        "words": len(words),
        "replacement_characters": content.count("\ufffd"),
        "whitespace_percent": round(100 * (len(content) - len(visible)) / len(content), 2) if content else 0.0,
        "has_usable_text": len(words) >= 3 and len(visible) >= 20,
    }
