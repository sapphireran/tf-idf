"""TF, IDF, and TF-IDF variants. Classic ln(N/df) is the gold formula."""

from __future__ import annotations

import math
from typing import Iterable, Mapping

VARIANTS = ("classic", "smooth", "sklearnish", "bm25-idf")


def normalized_tf(counts: Mapping[str, int], word_count: int) -> dict[str, float]:
    if word_count <= 0:
        return {term: 0.0 for term in counts}
    return {term: count / word_count for term, count in counts.items()}


def idf_value(n: int, df: int, variant: str = "classic") -> float:
    if df <= 0:
        raise ValueError("df must be positive")
    if n <= 0:
        raise ValueError("N must be positive")
    if variant == "classic":
        return math.log(n / df)
    if variant == "smooth":
        return math.log(n / (df + 1))
    if variant == "sklearnish":
        return math.log((n + 1) / (df + 1)) + 1.0
    if variant in ("bm25-idf", "bm25"):
        return math.log((n - df + 0.5) / (df + 0.5))
    raise ValueError(f"unknown IDF variant: {variant}")


def idf_map(
    df: Mapping[str, int], n: int, variant: str = "classic"
) -> dict[str, float]:
    return {term: idf_value(n, docs, variant) for term, docs in df.items()}


def tfidf_map(
    tf: Mapping[str, float], idf: Mapping[str, float]
) -> dict[str, float]:
    return {term: tf[term] * idf.get(term, 0.0) for term in tf}


def document_frequencies(count_maps: Iterable[Mapping[str, int]]) -> dict[str, int]:
    df: dict[str, int] = {}
    for counts in count_maps:
        for term in counts:
            df[term] = df.get(term, 0) + 1
    return df


def infer_word_count(tf: Mapping[str, float]) -> int:
    """Recover Perl word_count from a gold TF table (min TF is 1/word_count)."""
    positive = [value for value in tf.values() if value > 0]
    if not positive:
        return 0
    return max(1, round(1.0 / min(positive)))


def raw_tf_from_normalized(
    tf: Mapping[str, float], word_count: int
) -> dict[str, int]:
    return {term: int(round(value * word_count)) for term, value in tf.items()}
