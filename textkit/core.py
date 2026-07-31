def word_count(text: str) -> int:
    """Count whitespace-separated words in text."""
    return len(text.split())


def initials(name: str) -> str:
    """Return uppercase initials of a name.

    Each whitespace-separated word contributes its first character,
    uppercased and followed by a dot. A blank name yields an empty string.

    Example:
        >>> initials("ada lovelace")
        'A.L.'
    """
    return "".join(f"{word[0].upper()}." for word in name.split())
