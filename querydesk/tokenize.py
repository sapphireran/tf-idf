"""Perl-compatible tokenizer for tf-idf-values.pl."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, Iterator

# Close stand-in for Perl's [\h\v]+ after chomp (space, tab, vertical tabs, NBSP).
_WS = re.compile(r"[\t\n\x0b\x0c\r \u00a0]+")
_NON_ALNUM = re.compile(r"[^a-zA-Z0-9\s]")
_SPACES = re.compile(r" +")


def normalize_line(line: str) -> str:
    """Mirror chomp + whitespace collapse + lowercase + strip punctuation."""
    line = line.rstrip("\n")
    if line.endswith("\r"):
        line = line[:-1]
    line = _WS.sub(" ", line)
    line = line.lower()
    line = _NON_ALNUM.sub("", line)
    return line


def split_fields(normalized: str) -> list[str]:
    """Perl split(/ +/, ...) including a leading empty field, dropping trailers."""
    if normalized == "":
        return []
    parts = _SPACES.split(normalized)
    while parts and parts[-1] == "":
        parts.pop()
    return parts


def iter_fields(lines: Iterable[str]) -> Iterator[str]:
    for line in lines:
        yield from split_fields(normalize_line(line))


def count_document(lines: Iterable[str]) -> tuple[dict[str, int], int]:
    """Return (raw term counts, Perl word_count).

    Empty split fields increment word_count and are not stored as terms.
    """
    counts: dict[str, int] = {}
    word_count = 0
    for field in iter_fields(lines):
        word_count += 1
        if field == "":
            continue
        counts[field] = counts.get(field, 0) + 1
    return counts, word_count


def count_path(path: Path) -> tuple[dict[str, int], int]:
    with path.open(encoding="utf-8", errors="replace") as handle:
        return count_document(handle)


def count_text(text: str) -> tuple[dict[str, int], int]:
    return count_document(text.splitlines(keepends=True))


def list_text_files(directory: Path) -> list[Path]:
    """Non-hidden files, sorted — the eighteen Gutenberg texts, not .DS_Store."""
    return sorted(
        path
        for path in directory.iterdir()
        if path.is_file() and not path.name.startswith(".")
    )


def perl_last_index_n(directory: Path) -> int:
    """Approximate $#files after readdir (includes . and ..)."""
    names = list(directory.iterdir())
    return len(names) + 1  # +2 for . and .., then last index is count-1
