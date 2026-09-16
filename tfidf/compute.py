"""Build TF, IDF, and TF-IDF tables from a directory of plain-text documents."""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Literal, Sequence

from .tokenize import iter_corpus_files, tokenize_document

IdfMode = Literal["raw", "smooth"]


@dataclass(frozen=True)
class DocumentVector:
    """Per-document weights for one file in the corpus."""

    name: str
    token_count: int
    raw_tf: dict[str, int]
    tf: dict[str, float]
    tfidf: dict[str, float]

    def top_terms(self, n: int = 10) -> list[tuple[str, float]]:
        ranked = sorted(self.tfidf.items(), key=lambda item: (-item[1], item[0]))
        return ranked[:n]


@dataclass(frozen=True)
class TfidfIndex:
    """Corpus-level IDF plus one vector per document."""

    n_documents: int
    df: dict[str, int]
    idf: dict[str, float]
    documents: tuple[DocumentVector, ...]
    docs_for_term: dict[str, tuple[str, ...]]
    idf_mode: str

    def document(self, name: str) -> DocumentVector:
        for doc in self.documents:
            if doc.name == name:
                return doc
        known = ", ".join(doc.name for doc in self.documents)
        raise KeyError(f"unknown document {name!r}; have: {known}")

    def top_terms(self, name: str, n: int = 10) -> list[tuple[str, float]]:
        return self.document(name).top_terms(n)

    def cosine(self, left: str, right: str) -> float:
        """Cosine similarity between two document TF-IDF vectors."""
        return cosine_sparse(self.document(left).tfidf, self.document(right).tfidf)


def idf_value(n_documents: int, df: int, mode: IdfMode) -> float:
    """Return inverse document frequency for one term.

    * ``raw``    — ``log(N / df)``, the formula used by ``tf-idf-values.pl``
    * ``smooth`` — ``log((N + 1) / (df + 1)) + 1``, the sklearn default shape
    """
    if n_documents <= 0:
        raise ValueError("n_documents must be positive")
    if df <= 0:
        raise ValueError("document frequency must be positive for terms that exist")
    if mode == "raw":
        return math.log(n_documents / df)
    if mode == "smooth":
        return math.log((n_documents + 1) / (df + 1)) + 1.0
    raise ValueError(f"unknown idf mode: {mode!r}")


def build_index(
    input_dir: str | Path,
    *,
    idf_mode: IdfMode = "raw",
    perl_compat: bool = False,
) -> TfidfIndex:
    """Compute TF-IDF for every non-hidden file in ``input_dir``."""
    files = iter_corpus_files(input_dir)
    if not files:
        raise ValueError(f"no documents found in {input_dir}")

    tokenized: list[tuple[str, list[str], int]] = []
    for path in files:
        tokens, denom = tokenize_document(path, perl_compat=perl_compat)
        tokenized.append((path.name, tokens, denom))

    return build_index_from_documents(tokenized, idf_mode=idf_mode)


def build_index_from_documents(
    documents: Sequence[tuple[str, Sequence[str], int]],
    *,
    idf_mode: IdfMode = "raw",
) -> TfidfIndex:
    """Build an index from ``(name, tokens, token_count)`` triples.

    ``token_count`` is the TF denominator. It usually equals ``len(tokens)``;
    Perl-compat mode may pass a larger count when empty split fields exist.
    """
    if not documents:
        raise ValueError("documents must not be empty")

    docs_for_term: dict[str, list[str]] = defaultdict(list)
    prepared: list[tuple[str, Counter[str], int]] = []
    for name, tokens, token_count in documents:
        if token_count <= 0:
            raise ValueError(f"document {name!r} has no tokens")
        counts = Counter(tokens)
        prepared.append((name, counts, token_count))
        for term in counts:
            docs_for_term[term].append(name)

    n_documents = len(prepared)
    df = {term: len(names) for term, names in docs_for_term.items()}
    idf = {term: idf_value(n_documents, freq, idf_mode) for term, freq in df.items()}

    vectors: list[DocumentVector] = []
    for name, counts, token_count in prepared:
        tf = {term: raw / token_count for term, raw in counts.items()}
        tfidf = {term: tf[term] * idf[term] for term in counts}
        vectors.append(
            DocumentVector(
                name=name,
                token_count=token_count,
                raw_tf=dict(counts),
                tf=tf,
                tfidf=tfidf,
            )
        )

    frozen_docs_for_term = {
        term: tuple(names) for term, names in sorted(docs_for_term.items())
    }
    return TfidfIndex(
        n_documents=n_documents,
        df=df,
        idf=idf,
        documents=tuple(vectors),
        docs_for_term=frozen_docs_for_term,
        idf_mode=idf_mode,
    )


def cosine_sparse(left: dict[str, float], right: dict[str, float]) -> float:
    """Cosine similarity of two sparse weight dictionaries."""
    if not left or not right:
        return 0.0
    dot = 0.0
    small, large = (left, right) if len(left) <= len(right) else (right, left)
    for term, weight in small.items():
        other = large.get(term)
        if other:
            dot += weight * other
    left_norm = math.sqrt(sum(weight * weight for weight in left.values()))
    right_norm = math.sqrt(sum(weight * weight for weight in right.values()))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return dot / (left_norm * right_norm)


def score_query(
    index: TfidfIndex,
    query: str,
    *,
    perl_compat: bool = False,
) -> list[tuple[str, float]]:
    """Rank corpus documents against a free-text query.

    The query is tokenized with the same rules as the documents. IDF weights
    come from the corpus (unseen query terms are ignored). Query TF is
    normalized by the query's own token count.
    """
    tokens, token_count = tokenize_document(query, perl_compat=perl_compat)
    if token_count <= 0:
        raise ValueError("query produced no tokens")
    counts = Counter(tokens)
    query_tfidf: dict[str, float] = {}
    for term, raw in counts.items():
        if term not in index.idf:
            continue
        query_tfidf[term] = (raw / token_count) * index.idf[term]
    ranked = [
        (doc.name, cosine_sparse(query_tfidf, doc.tfidf)) for doc in index.documents
    ]
    ranked.sort(key=lambda item: (-item[1], item[0]))
    return ranked


def pairwise_cosine(index: TfidfIndex) -> list[tuple[str, str, float]]:
    """Upper-triangle cosine similarities, highest first."""
    names = [doc.name for doc in index.documents]
    pairs: list[tuple[str, str, float]] = []
    for i, left in enumerate(names):
        for right in names[i + 1 :]:
            pairs.append((left, right, index.cosine(left, right)))
    pairs.sort(key=lambda item: (-item[2], item[0], item[1]))
    return pairs


def format_top_table(
    rows: Iterable[tuple[str, float]],
    *,
    precision: int = 6,
) -> str:
    """Render ``(term, score)`` rows as a GitHub-flavored markdown table."""
    lines = ["| term | score |", "| --- | ---: |"]
    for term, score in rows:
        lines.append(f"| {term} | {score:.{precision}f} |")
    return "\n".join(lines)
