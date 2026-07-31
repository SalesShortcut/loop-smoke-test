def word_count(text: str) -> int:
    """Count whitespace-separated words in text."""
    return len(text.split())


def shout(text: str) -> str:
    """Uppercase text and make sure it ends with a single exclamation mark.

    Example:
        >>> shout("hello")
        'HELLO!'
    """
    up = text.upper()
    return up if up.endswith("!") else up + "!"
