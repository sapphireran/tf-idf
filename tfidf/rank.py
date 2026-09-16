"""Query ranking over a CorpusIndex."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Sequence

from .index import CorpusIndex
from .tokenize import tokenize_query
from .weights import document_weights, idf, tf as tf_weight


@dataclass
class RankedDocument:
    name: str
    score: float
    note: str = ""


def _dot(a: Dict[str, float], b: Dict[str, float]) -> float:
    if len(a) > len(b):
        a, b = b, a
    return sum(weight * b.get(term, 0.0) for term, weight in a.items())


def _norm(vec: Dict[str, float]) -> float:
    return math.sqrt(sum(weight * weight for weight in vec.values()))


def query_vector(
    query_tokens: Sequence[str],
    index: CorpusIndex,
    *,
    idf_flavor: str = "classic",
    tf_flavor: str = "normalized",
) -> Dict[str, float]:
    from collections import Counter

    counts = Counter(query_tokens)
    idf_by_term = {
        term: idf(index.df.get(term, 0), index.n_docs, idf_flavor) for term in counts
    }
    return document_weights(
        counts,
        len(query_tokens),
        idf_by_term,
        tf_flavor=tf_flavor,
        avgdl=index.avgdl,
    )


def rank_query(
    query: str,
    index: CorpusIndex,
    *,
    scheme: str = "cosine",
    idf_flavor: str = "classic",
    tf_flavor: str = "normalized",
    k: int = 10,
) -> List[RankedDocument]:
    """Rank documents for ``query``.

    ``scheme`` is one of ``cosine``, ``dot``, or ``bm25``.
    """
    tokens = tokenize_query(query, tokenizer=index.tokenizer)
    if not tokens:
        return []

    if scheme == "bm25":
        return _rank_bm25(tokens, index, k=k)

    q_vec = query_vector(
        tokens,
        index,
        idf_flavor=idf_flavor,
        tf_flavor=tf_flavor,
    )
    q_norm = _norm(q_vec)
    idf_table = index.idf_table(idf_flavor)
    ranked: List[RankedDocument] = []
    for doc in index.documents:
        d_vec = document_weights(
            doc.counts,
            doc.length,
            idf_table,
            tf_flavor=tf_flavor,
            avgdl=index.avgdl,
        )
        product = _dot(q_vec, d_vec)
        note = ""
        if scheme == "dot":
            score = product
        elif scheme == "cosine":
            d_norm = _norm(d_vec)
            if q_norm == 0.0 or d_norm == 0.0:
                score = 0.0
                note = "empty_vector"
            else:
                score = product / (q_norm * d_norm)
        else:
            raise ValueError(f"unknown scheme: {scheme!r}")
        ranked.append(RankedDocument(name=doc.name, score=score, note=note))
    ranked.sort(key=lambda row: (-row.score, row.name))
    return ranked[:k]


def _rank_bm25(
    query_tokens: Sequence[str],
    index: CorpusIndex,
    *,
    k: int,
    k1: float = 1.2,
    b: float = 0.75,
) -> List[RankedDocument]:
    from collections import Counter

    q_counts = Counter(query_tokens)
    avgdl = index.avgdl
    ranked: List[RankedDocument] = []
    for doc in index.documents:
        score = 0.0
        for term, qtf in q_counts.items():
            df = index.df.get(term, 0)
            idf_w = idf(df, index.n_docs, "bm25")
            tf_w = tf_weight(
                doc.counts.get(term, 0),
                doc.length,
                "bm25",
                avgdl=avgdl,
                k1=k1,
                b=b,
            )
            # Repeat the term in the query → add the contribution again.
            score += qtf * idf_w * tf_w
        ranked.append(RankedDocument(name=doc.name, score=score))
    ranked.sort(key=lambda row: (-row.score, row.name))
    return ranked[:k]
