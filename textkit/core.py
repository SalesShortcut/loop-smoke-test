def word_count(text: str) -> int:
    """Count whitespace-separated words in text."""
    return len(text.split())


def truncate(text: str, width: int) -> str:
    """Truncate text to width chars, ending with an ellipsis when cut.

    Raises:
        ValueError: if width is not positive.

    Example:
        >>> truncate("hello world", 8)
        'hello w…'
    """
    if width <= 0:
        raise ValueError("width must be positive")
    if len(text) <= width:
        return text
    return text[: width - 1] + "…"
