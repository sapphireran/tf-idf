"""TF, IDF, and TF-IDF flavors used in the personal notebook."""

from __future__ import annotations

import math
from typing import Dict, Mapping

IDF_FLAVORS = ("classic", "smooth", "probabilistic", "bm25")
TF_FLAVORS = ("raw", "normalized", "log", "boolean", "bm25")


def tf(
    count: float,
    doc_length: float,
    flavor: str = "normalized",
    *,
    max_count: float = 0.0,
    avgdl: float = 0.0,
    k1: float = 1.2,
    b: float = 0.75,
) -> float:
    """Return a term-frequency weight."""
    if count < 0:
        raise ValueError("count must be >= 0")
    if flavor == "raw":
        return float(count)
    if flavor == "normalized":
        if doc_length <= 0:
            return 0.0
        return float(count) / float(doc_length)
    if flavor == "log":
        if count <= 0:
            return 0.0
        return 1.0 + math.log(float(count))
    if flavor == "boolean":
        return 1.0 if count > 0 else 0.0
    if flavor == "augmented":
        if max_count <= 0:
            return 0.0
        return 0.5 + 0.5 * (float(count) / float(max_count))
    if flavor == "bm25":
        if count <= 0:
            return 0.0
        length_norm = 1.0
        if avgdl > 0 and doc_length > 0:
            length_norm = 1.0 - b + b * (float(doc_length) / float(avgdl))
        denom = float(count) + k1 * length_norm
        if denom == 0:
            return 0.0
        return (float(count) * (k1 + 1.0)) / denom
    raise ValueError(f"unknown tf flavor: {flavor!r}")


def idf(
    df: float,
    n_docs: float,
    flavor: str = "classic",
) -> float:
    """Return an inverse-document-frequency weight.

    Unseen terms (df == 0) return 0.0 for every flavor so a query
    token that never occurred on the shelf is a no-op rather than
    an exception.
    """
    if n_docs <= 0:
        raise ValueError("n_docs must be > 0")
    if df <= 0:
        return 0.0
    if df > n_docs:
        raise ValueError("df cannot exceed n_docs")

    if flavor == "classic":
        return math.log(n_docs / df)
    if flavor == "smooth":
        return math.log((n_docs + 1.0) / (df + 1.0)) + 1.0
    if flavor == "probabilistic":
        if df >= n_docs:
            # log((N-N)/N) is -inf. Notebook choice: treat as 0.
            return 0.0
        return math.log((n_docs - df) / df)
    if flavor == "bm25":
        # Lucene-style: log(1 + (N - df + 0.5)/(df + 0.5)) stays positive
        # even when df == N. The RSJ form without the inner +1 can go
        # negative on majority-shelf terms.
        return math.log(1.0 + (n_docs - df + 0.5) / (df + 0.5))
    raise ValueError(f"unknown idf flavor: {flavor!r}")


def tfidf(tf_weight: float, idf_weight: float) -> float:
    return float(tf_weight) * float(idf_weight)


def document_weights(
    counts: Mapping[str, int],
    doc_length: int,
    idf_by_term: Mapping[str, float],
    *,
    tf_flavor: str = "normalized",
    avgdl: float = 0.0,
    k1: float = 1.2,
    b: float = 0.75,
) -> Dict[str, float]:
    """Weight every term in one document."""
    max_count = max(counts.values()) if counts else 0
    out: Dict[str, float] = {}
    for term, count in counts.items():
        tf_w = tf(
            count,
            doc_length,
            tf_flavor,
            max_count=max_count,
            avgdl=avgdl,
            k1=k1,
            b=b,
        )
        out[term] = tfidf(tf_w, idf_by_term.get(term, 0.0))
    return out
