"""Sparse dot products and cosine similarity over tf * idf maps."""

from __future__ import annotations

from math import sqrt

from .tokenize import tokenize_text
from .weights import compute_tf


def dot(left: dict[str, float], right: dict[str, float]) -> float:
    if len(left) > len(right):
        left, right = right, left
    return sum(weight * right.get(token, 0.0) for token, weight in left.items())


def _norm(vector: dict[str, float]) -> float:
    return sqrt(sum(weight * weight for weight in vector.values()))


def cosine(left: dict[str, float], right: dict[str, float]) -> float:
    left_norm = _norm(left)
    right_norm = _norm(right)
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return dot(left, right) / (left_norm * right_norm)


def boolean_vector(weights: dict[str, float]) -> dict[str, float]:
    return {token: 1.0 for token, weight in weights.items() if weight != 0.0}


def rank_neighbors(
    documents: dict[str, dict[str, float]],
    *,
    mode: str = "tfidf",
) -> list[tuple[str, str, float]]:
    """All unordered pairs, highest cosine first."""
    if mode not in {"tfidf", "boolean"}:
        raise ValueError("mode must be 'tfidf' or 'boolean'")
    names = sorted(documents)
    vectors = {
        name: documents[name] if mode == "tfidf" else boolean_vector(documents[name])
        for name in names
    }
    pairs: list[tuple[str, str, float]] = []
    for i, left_name in enumerate(names):
        for right_name in names[i + 1 :]:
            score = cosine(vectors[left_name], vectors[right_name])
            pairs.append((left_name, right_name, score))
    pairs.sort(key=lambda row: (-row[2], row[0], row[1]))
    return pairs


def query_vector(
    query: str,
    idf: dict[str, float],
    *,
    count_empty_tokens: bool = False,
) -> dict[str, float]:
    """Treat a query string as a tiny document against corpus IDF."""
    stats = tokenize_text(query, count_empty_tokens=count_empty_tokens)
    tf = compute_tf(stats)
    return {token: weight * idf[token] for token, weight in tf.items() if token in idf}
