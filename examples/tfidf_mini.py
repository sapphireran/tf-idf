"""Minimal tf-idf that mirrors the personal Perl toy in this repo.

Tokenization follows tf-idf-values.pl:
  collapse whitespace, lowercase, drop non-alphanumeric, split on spaces.

Scoring follows the same product:
  tf(t, d)  = count(t, d) / tokens(d)
  idf(t)    = ln(N / df(t))
  tfidf     = tf * idf

N is the number of documents actually parsed (not Perl's $#files).
See docs/known-quirks.md for the empty-token denominator.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from pathlib import Path
from typing import Iterable

_NON_ALNUM = re.compile(r"[^a-zA-Z0-9\s]")
_WHITESPACE = re.compile(r"\s+")
_SPACES = re.compile(r" +")


def tokenize(text: str) -> list[str]:
    """Return the split fields after the same cleaning the Perl script does.

    Order matches tf-idf-values.pl: collapse whitespace, lowercase, drop
    non-alphanumeric, then split on one or more spaces. Perl's split drops
    trailing empty fields but keeps a leading empty field, so a line that
    starts with a space still increments the tf denominator.
    """
    cleaned: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.rstrip("\n\r")
        line = _WHITESPACE.sub(" ", line)
        line = line.lower()
        line = _NON_ALNUM.sub("", line)
        if line == "":
            continue
        fields = _SPACES.split(line)
        while fields and fields[-1] == "":
            fields.pop()
        cleaned.extend(fields)
    return cleaned


def nonempty_tokens(fields: Iterable[str]) -> list[str]:
    return [t for t in fields if t]


def term_frequency(fields: list[str], *, faithful: bool = True) -> dict[str, float]:
    """Normalized tf. faithful=True counts empty fields in the denominator."""
    tokens = nonempty_tokens(fields)
    denom = len(fields) if faithful else len(tokens)
    if denom == 0:
        return {}
    counts = Counter(tokens)
    return {term: count / denom for term, count in counts.items()}


def document_frequency(docs: dict[str, list[str]]) -> dict[str, set[str]]:
    """term -> set of document names that contain the term at least once."""
    df: dict[str, set[str]] = {}
    for name, fields in docs.items():
        for term in set(nonempty_tokens(fields)):
            df.setdefault(term, set()).add(name)
    return df


def inverse_document_frequency(
    df: dict[str, set[str]], n_docs: int
) -> dict[str, float]:
    if n_docs <= 0:
        raise ValueError("n_docs must be positive")
    idf = {}
    for term, names in df.items():
        present = len(names)
        if present == 0:
            continue
        idf[term] = math.log(n_docs / present)
    return idf


def tfidf_table(
    tf: dict[str, float], idf: dict[str, float]
) -> dict[str, float]:
    return {term: tf[term] * idf.get(term, 0.0) for term in tf}


def load_corpus(directory: Path) -> dict[str, str]:
    texts = {}
    for path in sorted(directory.iterdir()):
        if path.name.startswith(".") or not path.is_file():
            continue
        texts[path.name] = path.read_text(encoding="utf-8")
    return texts


def analyze_texts(
    texts: dict[str, str], *, faithful: bool = True
) -> dict:
    """Return token fields, tf, df, idf, and per-document tf-idf."""
    fields = {name: tokenize(text) for name, text in texts.items()}
    tfs = {name: term_frequency(toks, faithful=faithful) for name, toks in fields.items()}
    df = document_frequency(fields)
    idf = inverse_document_frequency(df, n_docs=len(fields))
    tfidf = {name: tfidf_table(tfs[name], idf) for name in fields}
    return {
        "fields": fields,
        "tf": tfs,
        "df": df,
        "idf": idf,
        "tfidf": tfidf,
        "n_docs": len(fields),
        "faithful": faithful,
    }


def analyze_directory(directory: Path, *, faithful: bool = True) -> dict:
    return analyze_texts(load_corpus(directory), faithful=faithful)


def ranked(weights: dict[str, float], n: int | None = None) -> list[tuple[str, float]]:
    rows = sorted(weights.items(), key=lambda item: (-item[1], item[0]))
    if n is not None:
        rows = rows[:n]
    return rows


def cosine(a: dict[str, float], b: dict[str, float]) -> float:
    """Cosine of two sparse tf-idf vectors (term -> weight)."""
    if not a or not b:
        return 0.0
    dot = 0.0
    for term, weight in a.items():
        other = b.get(term)
        if other:
            dot += weight * other
    norm_a = math.sqrt(sum(w * w for w in a.values()))
    norm_b = math.sqrt(sum(w * w for w in b.values()))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def pairwise_cosine(
    vectors: dict[str, dict[str, float]],
) -> list[tuple[str, str, float]]:
    """All unordered pairs, highest cosine first."""
    names = sorted(vectors)
    pairs = []
    for i, left in enumerate(names):
        for right in names[i + 1 :]:
            pairs.append((left, right, cosine(vectors[left], vectors[right])))
    pairs.sort(key=lambda item: (-item[2], item[0], item[1]))
    return pairs
