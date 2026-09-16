"""Tokenizers for the personal TF-IDF lab.

`simple` is the default used by tests and the worked example.
`perl_legacy` follows tf-idf-values.pl closely enough to discuss
the 2012 tables without claiming bit-identical output on every file.
"""

from __future__ import annotations

import re
from typing import Iterable, List, Sequence, Tuple

SIMPLE_TOKEN = re.compile(r"[a-z0-9]+")
# Perl: $txt =~ s/[\h\v]+/ /g; then strip non-alnum; then split(/ +/).
PERL_WS = re.compile(r"[ \t\n\r\f\v]+")
PERL_NON_ALNUM = re.compile(r"[^a-zA-Z0-9 ]")


def simple_tokens(text: str) -> List[str]:
    """Lowercase and keep runs of ASCII letters and digits."""
    return SIMPLE_TOKEN.findall(text.lower())


def perl_legacy_tokens(text: str) -> Tuple[List[str], int]:
    """Approximate the 2012 Perl tokenizer.

    Returns ``(kept_tokens, word_count)``. ``word_count`` includes empty
    strings produced by ``split(/ +/)``, matching the specimen's
    length denominator. Kept tokens omit those empties.
    """
    kept: List[str] = []
    word_count = 0
    # Process the whole text line-by-line the way the Perl <> loop did.
    lines = text.splitlines()
    if not lines and text:
        lines = [text]
    for raw in lines:
        txt = PERL_WS.sub(" ", raw)
        txt = txt.lower()
        txt = PERL_NON_ALNUM.sub("", txt)
        pieces = txt.split(" ")
        for piece in pieces:
            word_count += 1
            if piece != "":
                kept.append(piece)
    return kept, word_count


def tokenize(
    text: str,
    tokenizer: str = "simple",
) -> Tuple[List[str], int]:
    """Return ``(tokens, length_denominator)`` for a named tokenizer."""
    if tokenizer == "simple":
        tokens = simple_tokens(text)
        return tokens, len(tokens)
    if tokenizer == "perl_legacy":
        return perl_legacy_tokens(text)
    raise ValueError(f"unknown tokenizer: {tokenizer!r}")


def tokenize_query(text: str, tokenizer: str = "simple") -> List[str]:
    tokens, _ = tokenize(text, tokenizer=tokenizer)
    return tokens


def drop_stopwords(tokens: Sequence[str], stopwords: Iterable[str]) -> List[str]:
    banned = {s.lower() for s in stopwords}
    return [t for t in tokens if t not in banned]
