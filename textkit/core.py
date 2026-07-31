import re

_SEPARATOR_RUN = re.compile(r"[^a-z0-9]+")


def word_count(text: str) -> int:
    """Count whitespace-separated words in text."""
    return len(text.split())


def slugify(text: str) -> str:
    """Turn text into a URL-safe slug of a-z, 0-9 and hyphens.

    Any run of other characters becomes a single hyphen; leading and
    trailing hyphens are trimmed. Non-ASCII characters are not
    transliterated, so they are treated as separators.
    """
    return _SEPARATOR_RUN.sub("-", text.lower()).strip("-")
