"""Tokenizers for the 2012 Perl pipeline and a slightly cleaner study mode.

The original scripts in the repository root process one physical line at a
time. After ``chomp``, they:

1. collapse horizontal/vertical whitespace to a single space
2. lowercase ASCII letters
3. drop every character that is not alphanumeric or whitespace
4. ``split(/ +/)`` the line

Perl's ``split`` without a limit strips trailing empty fields but keeps a
leading empty field. The 2012 script increments ``$word_count`` for every
field, including that leading empty, then ignores empty keys when filling
``%tf``. Study-mode tokenization below matches the *kept* tokens and counts
only those, which is what you want when you are not reproducing the
checked-in ``output/`` tables cell-for-cell.
"""

from __future__ import annotations

import re
from typing import Iterable

_NON_TOKEN = re.compile(r"[^a-z0-9\s]")
_HORIZ = re.compile(r"[^\S\n\r]+")


def _prepare_line(line: str) -> str:
    collapsed = _HORIZ.sub(" ", line.replace("\v", " ").replace("\f", " "))
    return _NON_TOKEN.sub("", collapsed.lower())


def tokenize_perl_line(line: str) -> tuple[list[str], int]:
    """Return (kept tokens, Perl-style word_count) for one physical line."""
    prepared = _prepare_line(line)
    parts = re.split(r" +", prepared)
    while parts and parts[-1] == "":
        parts.pop()
    kept = [part for part in parts if part]
    return kept, len(parts)


def tokenize_perl(text: str) -> tuple[list[str], int]:
    """Tokenize a whole document the way ``tf-idf-values.pl`` walks a file."""
    tokens: list[str] = []
    word_count = 0
    for raw in text.splitlines():
        kept, count = tokenize_perl_line(raw.rstrip("\n\r"))
        tokens.extend(kept)
        word_count += count
    return tokens, word_count


def tokenize(text: str) -> list[str]:
    """Study-mode tokens: same character class, empty fields discarded."""
    tokens, _ = tokenize_perl(text)
    return tokens


def token_counts(tokens: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for token in tokens:
        counts[token] = counts.get(token, 0) + 1
    return counts
