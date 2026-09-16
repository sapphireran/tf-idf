"""tf, df, idf, and tf * idf using this repository's formulas."""

from __future__ import annotations

from dataclasses import dataclass
from math import log
from pathlib import Path

from .tokenize import TokenStats, tokenize_document


@dataclass(frozen=True)
class PipelineResult:
    """In-memory result of walking a directory of documents."""

    documents: tuple[str, ...]
    stats: dict[str, TokenStats]
    tf: dict[str, dict[str, float]]
    df: dict[str, set[str]]
    idf: dict[str, float]
    tfidf: dict[str, dict[str, float]]

    @property
    def n_documents(self) -> int:
        return len(self.documents)


def compute_tf(stats: TokenStats) -> dict[str, float]:
    return stats.tf()


def compute_idf(df: dict[str, set[str]], n_documents: int) -> dict[str, float]:
    """``idf(t) = ln(N / df(t))`` with ``N`` equal to processed documents."""
    if n_documents <= 0:
        raise ValueError("n_documents must be positive")
    idf: dict[str, float] = {}
    for token, docs in df.items():
        document_frequency = len(docs)
        if document_frequency <= 0:
            continue
        idf[token] = log(n_documents / document_frequency)
    return idf


def compute_tfidf(
    tf: dict[str, dict[str, float]], idf: dict[str, float]
) -> dict[str, dict[str, float]]:
    product: dict[str, dict[str, float]] = {}
    for name, term_weights in tf.items():
        product[name] = {
            token: weight * idf[token]
            for token, weight in term_weights.items()
            if token in idf
        }
    return product


def run_pipeline(
    input_dir: Path,
    *,
    count_empty_tokens: bool = False,
    pattern: str = "*.txt",
) -> PipelineResult:
    """Walk ``input_dir`` and compute the four tables the Perl scripts write."""
    paths = sorted(
        path
        for path in input_dir.glob(pattern)
        if path.is_file() and not path.name.startswith(".")
    )
    if not paths:
        raise FileNotFoundError(f"no documents matching {pattern} in {input_dir}")

    stats: dict[str, TokenStats] = {}
    tf: dict[str, dict[str, float]] = {}
    df: dict[str, set[str]] = {}
    documents: list[str] = []

    for path in paths:
        name = path.name
        documents.append(name)
        token_stats = tokenize_document(path, count_empty_tokens=count_empty_tokens)
        stats[name] = token_stats
        tf[name] = compute_tf(token_stats)
        for token in token_stats.counts:
            df.setdefault(token, set()).add(name)

    idf = compute_idf(df, len(documents))
    tfidf = compute_tfidf(tf, idf)
    return PipelineResult(
        documents=tuple(documents),
        stats=stats,
        tf=tf,
        df=df,
        idf=idf,
        tfidf=tfidf,
    )
