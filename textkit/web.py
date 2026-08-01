"""Web playground for textkit: a single page over the core functions."""

from . import core

TRUNCATE_WIDTH = 20

OPERATIONS = {
    "slugify": core.slugify,
    "shout": core.shout,
    "initials": core.initials,
    "reverse_words": core.reverse_words,
    "truncate": lambda text: core.truncate(text, TRUNCATE_WIDTH),
}


def transform(op: str, text: str) -> str:
    """Apply the named textkit operation to text.

    Supported ops are the keys of OPERATIONS; `truncate` uses width
    TRUNCATE_WIDTH. An unknown op raises ValueError.

    Example:
        >>> transform("slugify", "Ada Lovelace")
        'ada-lovelace'
    """
    try:
        func = OPERATIONS[op]
    except KeyError:
        raise ValueError(f"unknown op: {op!r}") from None
    return func(text)
