"""Sliding-window passage retrieval over a single long text."""

from __future__ import annotations

from dataclasses import dataclass

from .index import Document, TfIdfIndex
from .tokenize import tokenize
from .weights import cosine


@dataclass(frozen=True)
class Passage:
    doc_id: str
    title: str
    start_token: int
    end_token: int
    text: str


def window_passages(
    text: str,
    *,
    source: str,
    window: int = 80,
    stride: int = 40,
    prefix: str = "pass",
) -> list[Document]:
    """Turn a long string into overlapping token windows.

    Windows are built from study-mode tokens, then the same token slice is
    joined back into a short document. This is coarse (punctuation is
    already gone) and that is fine for a personal retrieval lab.
    """
    if window <= 0 or stride <= 0:
        raise ValueError("window and stride must be positive")
    tokens = tokenize(text)
    docs: list[Document] = []
    if not tokens:
        return docs
    start = 0
    index = 0
    while start < len(tokens):
        end = min(len(tokens), start + window)
        chunk = tokens[start:end]
        if not chunk:
            break
        docs.append(
            Document(
                doc_id=f"{prefix}-{index:04d}",
                title=f"{source} tokens {start}:{end}",
                text=" ".join(chunk),
                source=source,
            )
        )
        index += 1
        if end == len(tokens):
            break
        start += stride
    return docs


def rank_passages(
    text: str,
    query: str,
    *,
    source: str,
    window: int = 80,
    stride: int = 40,
    k: int = 5,
    prefix: str = "pass",
) -> list[tuple[Passage, float]]:
    docs = window_passages(
        text, source=source, window=window, stride=stride, prefix=prefix
    )
    if not docs:
        return []
    index = TfIdfIndex(docs)
    ranked = index.rank(query, k=k)
    out: list[tuple[Passage, float]] = []
    for doc, score in ranked:
        tokens = doc.text.split()
        # Recover the token offsets from the title we stamped above.
        try:
            span = doc.title.rsplit("tokens ", 1)[1]
            start_s, end_s = span.split(":")
            start, end = int(start_s), int(end_s)
        except (IndexError, ValueError):
            start, end = 0, len(tokens)
        out.append(
            (
                Passage(
                    doc_id=doc.doc_id,
                    title=doc.title,
                    start_token=start,
                    end_token=end,
                    text=doc.text,
                ),
                score,
            )
        )
    return out


def rank_query_against(index: TfIdfIndex, query: str, k: int = 5):
    qv = index.query_vector(query)
    scored = [
        (doc, cosine(qv, index.vector(doc.doc_id))) for doc in index.documents
    ]
    scored.sort(key=lambda item: (-item[1], item[0].doc_id))
    return scored[:k]
