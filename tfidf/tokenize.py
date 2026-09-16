"""Line-oriented tokenization used by the examples and the Python CLI.

The original ``tf-idf-values.pl`` script is short and a little idiosyncratic.
This module documents those choices so the Python path can either:

* use a clean default (count only non-empty tokens), or
* approximate the Perl denominator (``--perl-compat``).

Perl, line by line:

1. ``chomp`` the newline
2. collapse horizontal/vertical whitespace runs to a single space
3. lowercase with ``tr/[A-Z]/[a-z]/`` (the brackets are in the set but map
   to themselves, so the effect is ordinary ASCII lowercasing)
4. strip every character that is not ASCII letter, digit, or whitespace
5. ``split(/ +/, $line)`` — trailing empty fields are discarded
6. increment ``$word_count`` for every remaining field, including a leading
   empty field when the cleaned line starts with a space
7. increment term frequency only when the field is non-empty
"""

from __future__ import annotations

import re
from pathlib import Path

# Close to Perl's \\h + \\v for the ASCII Gutenberg texts in this repo.
_WHITESPACE_RUN = re.compile(r"[\t\n\x0b\x0c\r \x85\xa0]+")
_NON_ALNUM = re.compile(r"[^a-z0-9\s]")
_SPACE_RUN = re.compile(r" +")


def normalize_text(text: str) -> str:
    """Apply the Perl cleanup rules to a single line (already chomped)."""
    collapsed = _WHITESPACE_RUN.sub(" ", text)
    lowered = collapsed.lower()
    return _NON_ALNUM.sub("", lowered)


def _perl_split(cleaned: str) -> list[str]:
    """Mimic Perl ``split(/ +/, $cleaned)`` with the default trailing-empty drop."""
    if cleaned == "":
        return []
    parts = _SPACE_RUN.split(cleaned)
    while parts and parts[-1] == "":
        parts.pop()
    return parts


def tokenize(text: str) -> list[str]:
    """Return non-empty tokens from a full string (newlines treated as space)."""
    cleaned = normalize_text(text.replace("\n", " "))
    return [part for part in _perl_split(cleaned) if part]


def tokenize_line(line: str, *, perl_compat: bool = False) -> tuple[list[str], int]:
    """Tokenize one chomped line.

    Returns ``(non_empty_tokens, denominator_increment)``.
    In default mode the denominator is the number of non-empty tokens.
    In Perl-compat mode the denominator is ``len(split(/ +/))``, which can
    include a leading empty field.
    """
    cleaned = normalize_text(line.rstrip("\n\r"))
    parts = _perl_split(cleaned)
    tokens = [part for part in parts if part]
    if perl_compat:
        return tokens, len(parts)
    return tokens, len(tokens)


def tokenize_document(
    source: str | Path,
    *,
    perl_compat: bool = False,
) -> tuple[list[str], int]:
    """Read a UTF-8 text file (or a raw string) and tokenize it line by line.

    Passing a string that does not exist as a path is treated as document
    text. That keeps the query-ranking examples free of temp files.
    """
    path = Path(source)
    if isinstance(source, Path) or path.is_file():
        text = path.read_text(encoding="utf-8", errors="replace")
    else:
        text = str(source)

    tokens: list[str] = []
    denominator = 0
    for raw_line in text.splitlines():
        line_tokens, increment = tokenize_line(raw_line, perl_compat=perl_compat)
        tokens.extend(line_tokens)
        denominator += increment
    return tokens, denominator


def iter_corpus_files(
    input_dir: str | Path,
    pattern: str = "*.txt",
) -> list[Path]:
    """List non-hidden files in ``input_dir`` matching ``pattern``.

    The default ``*.txt`` keeps README.md and other notes out of the
    corpus (the tiny-corpus folder ships a README next to the four
    documents). Hidden names are skipped, matching the Perl
    ``$f !~ /^\\./`` guard.
    """
    root = Path(input_dir)
    if not root.is_dir():
        raise FileNotFoundError(f"corpus directory not found: {root}")
    files = [
        path
        for path in root.glob(pattern)
        if path.is_file() and not path.name.startswith(".")
    ]
    return sorted(files, key=lambda path: path.name)
