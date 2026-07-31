def word_count(text: str) -> int:
    """Count whitespace-separated words in text."""
    return len(text.split())


def reverse_words(text: str) -> str:
    """Return the words of text in reverse order, joined by single spaces.

    Example:
        >>> reverse_words("a b c")
        'c b a'
    """
    return " ".join(text.split()[::-1])
