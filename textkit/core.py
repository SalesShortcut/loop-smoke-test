import re


def word_count(text: str) -> int:
    """Count whitespace-separated words in text."""
    return len(text.split())


def slugify(text: str) -> str:
    """Return a URL-safe slug built from text.

    Letters and digits are kept and lowercased, every other run of
    characters becomes a single hyphen.

    Example:
        >>> slugify("Ada Lovelace")
        'ada-lovelace'
    """
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def shout(text: str) -> str:
    """Return text in upper case.

    Example:
        >>> shout("ada lovelace")
        'ADA LOVELACE'
    """
    return text.upper()


def initials(name: str) -> str:
    """Return uppercase initials of a name.

    Each word contributes its first character, followed by a dot.

    Example:
        >>> initials("ada lovelace")
        'A.L.'
    """
    return "".join(word[0].upper() + "." for word in name.split())


def reverse_words(text: str) -> str:
    """Return text with the order of its words reversed.

    Example:
        >>> reverse_words("ada loved numbers")
        'numbers loved ada'
    """
    return " ".join(reversed(text.split()))


def truncate(text: str, width: int) -> str:
    """Shorten text to at most width characters, marking cuts with "...".

    Text no longer than width is returned unchanged. A width too small to
    hold the ellipsis yields as many dots as fit.

    Example:
        >>> truncate("Ada Lovelace was a mathematician", 20)
        'Ada Lovelace was...'
    """
    if len(text) <= width:
        return text
    if width <= 3:
        return "." * max(width, 0)
    return text[: width - 3].rstrip() + "..."
