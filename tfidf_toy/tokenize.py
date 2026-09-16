"""Line-oriented tokenizer matching the original Perl scripts closely.

See docs/tokenization.md for the product rules and the Perl length quirk.
"""

from __future__ import annotations

import re
from pathlib import Path

_WS = re.compile(r"\s+")
_NON_ALNUM = re.compile(r"[^a-z0-9\s]")


def tokenize_line(line: str, *, match_perl_length: bool = False) -> tuple[list[str], int]:
    """Tokenize one line.

    Returns ``(tokens, length_denominator)``. The denominator is the tf
    normalizer for this line: either the number of real tokens (default) or
    Perl's ``word_count`` including a leading empty field.
    """
    line = line.rstrip("\n\r")
    line = _WS.sub(" ", line)
    line = line.lower()
    line = _NON_ALNUM.sub("", line)

    if line == "" or line == " ":
        return [], 0

    if match_perl_length:
        parts = re.split(r" +", line)
        # Perl split(/ +/, ...) strips trailing empty fields, keeps leading.
        if parts and parts[-1] == "":
            parts = parts[:-1]
        if parts == [""]:
            return [], 0
        tokens = [p for p in parts if p]
        return tokens, len(parts)

    tokens = [part for part in line.split(" ") if part]
    return tokens, len(tokens)


def tokenize(text: str, *, match_perl_length: bool = False) -> tuple[list[str], int]:
    """Tokenize a full document. Length is the sum of per-line denominators."""
    tokens: list[str] = []
    length = 0
    # splitlines() drops the line break the same way Perl's <> + chomp does.
    lines = text.splitlines()
    if not lines and text:
        lines = [text]
    for line in lines:
        line_tokens, line_length = tokenize_line(line, match_perl_length=match_perl_length)
        tokens.extend(line_tokens)
        length += line_length
    return tokens, length


def load_corpus(directory: Path) -> dict[str, str]:
    """Load every non-hidden file in ``directory`` keyed by filename.

    UTF-8 is tried first; ``shakespeare-caesar.txt`` in this repo is latin-1,
    so a decode error falls back to ISO-8859-1.
    """
    directory = Path(directory)
    documents: dict[str, str] = {}
    for path in sorted(directory.iterdir()):
        if path.name.startswith("."):
            continue
        if not path.is_file():
            continue
        try:
            documents[path.name] = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            documents[path.name] = path.read_text(encoding="latin-1")
    if not documents:
        raise FileNotFoundError(f"no documents found in {directory}")
    return documents
