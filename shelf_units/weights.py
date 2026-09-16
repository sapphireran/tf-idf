"""Classic TF-IDF pieces used by the 2012 snapshot, plus one smooth variant.

The checked-in ``output/idf.txt`` values are

    idf(t) = ln(N / df(t))

with natural log, raw document frequency, and no +1 smoothing. Term
frequency in ``output/tf/`` is a length-normalized count:

    tf(t, d) = count(t, d) / word_count(d)

The original Perl script's ``word_count`` includes empty ``split`` fields;
study mode below uses ``len(tokens)`` unless a caller passes an explicit
denominator. The product is just ``tf * idf``. A term that appears in every
document has idf 0, which is why ``a`` / ``the`` / ``and`` print as ``0``
in the Gutenberg TF-IDF tables.
"""

from __future__ import annotations

import math
from typing import Mapping


def tf_normalized(count: int, word_count: int) -> float:
    if word_count <= 0:
        return 0.0
    return count / word_count


def tf_log(count: int) -> float:
    """1 + ln(count) for count > 0, else 0. Not used by the 2012 scripts."""
    if count <= 0:
        return 0.0
    return 1.0 + math.log(count)


def idf_classic(n_docs: int, df: int) -> float:
    """``ln(N / df)``. Matches the snapshot when ``N`` is the true file count."""
    if df <= 0 or n_docs <= 0:
        raise ValueError("idf_classic requires positive N and df")
    return math.log(n_docs / df)


def idf_smooth(n_docs: int, df: int) -> float:
    """``ln((N + 1) / (df + 1)) + 1`` — a common sklearn-ish smoother."""
    if df < 0 or n_docs <= 0:
        raise ValueError("idf_smooth requires N > 0 and df >= 0")
    return math.log((n_docs + 1) / (df + 1)) + 1.0


def tfidf_classic(count: int, word_count: int, n_docs: int, df: int) -> float:
    return tf_normalized(count, word_count) * idf_classic(n_docs, df)


def cosine(left: Mapping[str, float], right: Mapping[str, float]) -> float:
    if not left or not right:
        return 0.0
    if len(left) > len(right):
        left, right = right, left
    dot = 0.0
    for term, value in left.items():
        other = right.get(term)
        if other:
            dot += value * other
    if dot == 0.0:
        return 0.0
    norm_l = math.sqrt(sum(v * v for v in left.values()))
    norm_r = math.sqrt(sum(v * v for v in right.values()))
    if norm_l == 0.0 or norm_r == 0.0:
        return 0.0
    return dot / (norm_l * norm_r)
