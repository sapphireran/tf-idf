"""Rank queries against an Index and attribute the score to terms."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Mapping, Sequence

from .index import Index
from .tokenize import count_text
from .weights import idf_value, normalized_tf, tfidf_map

BM25_K1 = 1.2
BM25_B = 0.75


@dataclass(frozen=True)
class Hit:
    name: str
    score: float


@dataclass(frozen=True)
class Attribution:
    term: str
    query_weight: float
    doc_weight: float
    product: float


def dot(left: Mapping[str, float], right: Mapping[str, float]) -> float:
    if len(left) > len(right):
        left, right = right, left
    return sum(value * right.get(term, 0.0) for term, value in left.items())


def l2(vector: Mapping[str, float]) -> float:
    return math.sqrt(sum(value * value for value in vector.values()))


def cosine(left: Mapping[str, float], right: Mapping[str, float]) -> float:
    denom = l2(left) * l2(right)
    if denom == 0.0:
        return 0.0
    return dot(left, right) / denom


def query_tfidf(text: str, index: Index) -> tuple[dict[str, float], dict[str, int], int]:
    counts, word_count = count_text(text)
    tf = normalized_tf(counts, word_count)
    weights = tfidf_map(tf, index.idf)
    return weights, counts, word_count


def bm25_score(
    query_counts: Mapping[str, int],
    index: Index,
    doc_name: str,
    *,
    k1: float = BM25_K1,
    b: float = BM25_B,
) -> float:
    doc = index.docs[doc_name]
    avgdl = index.avgdl or 1.0
    score = 0.0
    for term, qf in query_counts.items():
        if qf <= 0:
            continue
        freq = doc.raw_tf.get(term, 0)
        if freq <= 0:
            continue
        df = index.df.get(term, 0)
        if df <= 0:
            continue
        idf = idf_value(index.n, df, "bm25-idf")
        denom = freq + k1 * (1.0 - b + b * doc.word_count / avgdl)
        score += idf * (freq * (k1 + 1.0)) / denom
    return score


def rank(
    text: str,
    index: Index,
    *,
    score: str = "cosine",
    top: int | None = None,
) -> list[Hit]:
    if score == "bm25":
        _, counts, _ = query_tfidf(text, index)
        hits = [
            Hit(name=name, score=bm25_score(counts, index, name))
            for name in index.docs
        ]
    else:
        qvec, _, _ = query_tfidf(text, index)
        hits = []
        for name, doc in index.docs.items():
            if score == "cosine":
                value = cosine(qvec, doc.tfidf)
            elif score == "dot":
                value = dot(qvec, doc.tfidf)
            else:
                raise ValueError(f"unknown score: {score}")
            hits.append(Hit(name=name, score=value))
    hits.sort(key=lambda hit: (-hit.score, hit.name))
    if top is not None:
        hits = hits[:top]
    return hits


def explain(
    text: str,
    index: Index,
    doc_name: str,
    *,
    top: int = 12,
) -> tuple[float, list[Attribution]]:
    if doc_name not in index.docs:
        raise KeyError(doc_name)
    qvec, _, _ = query_tfidf(text, index)
    dvec = index.docs[doc_name].tfidf
    rows = []
    for term, q_weight in qvec.items():
        d_weight = dvec.get(term, 0.0)
        product = q_weight * d_weight
        if product == 0.0 and d_weight == 0.0:
            continue
        rows.append(
            Attribution(
                term=term,
                query_weight=q_weight,
                doc_weight=d_weight,
                product=product,
            )
        )
    rows.sort(key=lambda row: (-row.product, row.term))
    return cosine(qvec, dvec), rows[:top]


def compare_rankings(
    text: str,
    index: Index,
    variants: Sequence[str],
    *,
    top: int = 5,
) -> dict[str, list[Hit]]:
    out: dict[str, list[Hit]] = {}
    for variant in variants:
        key = variant.strip()
        if not key:
            continue
        if key == "bm25":
            out[key] = rank(text, index, score="bm25", top=top)
            continue
        from .weights import idf_map, tfidf_map as _tfidf

        shifted = Index(
            n=index.n,
            variant=key,
            df=index.df,
            idf=idf_map(index.df, index.n, variant=key),
            docs=dict(index.docs),
            members=index.members,
        )
        # Rebuild document TF-IDF with the new IDF; keep raw TF.
        new_docs = {}
        for name, doc in index.docs.items():
            new_docs[name] = type(doc)(
                name=doc.name,
                raw_tf=doc.raw_tf,
                word_count=doc.word_count,
                tf=doc.tf,
                tfidf=_tfidf(doc.tf, shifted.idf),
            )
        shifted.docs = new_docs
        out[key] = rank(text, shifted, score="cosine", top=top)
    return out
