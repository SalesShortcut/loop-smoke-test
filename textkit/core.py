import re
import unicodedata

# Words that stay lowercase inside a title, unless they come first.
TITLE_CASE_CONNECTORS = frozenset({"a", "an", "the", "and", "or", "of", "in", "on"})


def word_count(text: str) -> int:
    """Count whitespace-separated words in text."""
    return len(text.split())


def slugify(text: str) -> str:
    """Return a URL-safe ASCII slug built from text.

    Accented Latin letters are reduced to their base letter (NFKD), then
    ASCII letters and digits are kept and lowercased; every other run of
    characters — including non-Latin scripts — becomes a single hyphen.

    Example:
        >>> slugify("Ada Lovelace")
        'ada-lovelace'
        >>> slugify("Café au lait")
        'cafe-au-lait'
    """
    ascii_text = (
        unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    )
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")


def shout(text: str) -> str:
    """Return text in upper case.

    Example:
        >>> shout("ada lovelace")
        'ADA LOVELACE'
    """
    return text.upper()


def title_case(text: str) -> str:
    """Return text in headline form, with connector words kept lowercase.

    Every whitespace-separated word gets an uppercase first character and a
    lowercase remainder. The connectors in TITLE_CASE_CONNECTORS stay
    lowercase unless they are the first word. Runs of whitespace collapse to
    a single space.

    Example:
        >>> title_case("ada lovelace and the analytical engine")
        'Ada Lovelace and the Analytical Engine'
    """
    return " ".join(
        word.lower()
        if index and word.lower() in TITLE_CASE_CONNECTORS
        else word[0].upper() + word[1:].lower()
        for index, word in enumerate(text.split())
    )


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
