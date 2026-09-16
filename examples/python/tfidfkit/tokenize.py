"""Tokenizer that can match the 2012 Perl normalizer.

The original script, ``tf-idf-values.pl``, does four things to each line
and then splits on spaces:

1. ``chomp``
2. collapse horizontal / vertical whitespace runs to a single space
3. lowercase ASCII letters
4. delete characters that are not letters, digits, or whitespace

Perl ``split(/ +/, ...)`` keeps a leading empty field. The original
script increments ``$word_count`` for that empty field but does not store
it as a token. ``count_empty_tokens`` reproduces that denominator.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import re

_WHITESPACE_RUN = re.compile(r"\s+")
_KEEP = re.compile(r"[^a-zA-Z0-9\s]")


def normalize_line(line: str) -> str:
    """Apply the Perl line normalizer to one raw line, without splitting."""
    text = line.rstrip("\r\n")
    text = _WHITESPACE_RUN.sub(" ", text)
    text = text.lower()
    text = _KEEP.sub("", text)
    return text


def tokenize_text(text: str, *, count_empty_tokens: bool = False) -> TokenStats:
    """Tokenize a whole document already loaded as a string."""
    counts: Counter[str] = Counter()
    denominator = 0
    for raw_line in text.splitlines(keepends=True):
        line = normalize_line(raw_line)
        if line == "":
            continue
        parts = line.split(" ")
        for part in parts:
            if part == "":
                if count_empty_tokens:
                    denominator += 1
                continue
            counts[part] += 1
            denominator += 1
    return TokenStats(counts=counts, token_count=denominator)


def tokenize_document(path: Path, *, count_empty_tokens: bool = False) -> TokenStats:
    """Tokenize a UTF-8 (or Latin-1 fallback) text file."""
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="latin-1")
    return tokenize_text(text, count_empty_tokens=count_empty_tokens)


@dataclass(frozen=True)
class TokenStats:
    """Per-document bag of tokens plus the TF denominator."""

    counts: Counter[str]
    token_count: int

    def tf(self) -> dict[str, float]:
        if self.token_count == 0:
            return {}
        return {token: count / self.token_count for token, count in self.counts.items()}
