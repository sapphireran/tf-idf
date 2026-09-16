"""Build or load a TF-IDF index (Gutenberg gold or a tiny corpus)."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from . import tables
from .tokenize import count_path, list_text_files, perl_last_index_n
from .weights import (
    document_frequencies,
    idf_map,
    infer_word_count,
    normalized_tf,
    raw_tf_from_normalized,
    tfidf_map,
)

NMode = Literal["texts", "perl-last-index"]
ROOT = Path(__file__).resolve().parent.parent


@dataclass
class Document:
    name: str
    raw_tf: dict[str, int]
    word_count: int
    tf: dict[str, float]
    tfidf: dict[str, float]


@dataclass
class Index:
    n: int
    variant: str
    df: dict[str, int]
    idf: dict[str, float]
    docs: dict[str, Document]
    members: dict[str, list[str]] = field(default_factory=dict)

    @property
    def avgdl(self) -> float:
        if not self.docs:
            return 0.0
        return sum(doc.word_count for doc in self.docs.values()) / len(self.docs)


def collection_size(corpus_dir: Path, n_mode: NMode) -> int:
    texts = list_text_files(corpus_dir)
    if n_mode == "texts":
        return len(texts)
    if n_mode == "perl-last-index":
        return perl_last_index_n(corpus_dir)
    raise ValueError(n_mode)


def build_index(
    corpus_dir: Path,
    *,
    variant: str = "classic",
    n_mode: NMode = "texts",
) -> Index:
    paths = list_text_files(corpus_dir)
    if not paths:
        raise FileNotFoundError(f"no text files in {corpus_dir}")
    raw_docs: list[tuple[str, dict[str, int], int]] = []
    for path in paths:
        counts, word_count = count_path(path)
        raw_docs.append((path.name, counts, word_count))
    n = collection_size(corpus_dir, n_mode)
    df = document_frequencies(counts for _, counts, _ in raw_docs)
    members: dict[str, list[str]] = {term: [] for term in df}
    for name, counts, _ in raw_docs:
        for term in counts:
            members[term].append(name)
    idf = idf_map(df, n, variant="bm25-idf" if variant == "bm25" else variant)
    docs: dict[str, Document] = {}
    for name, counts, word_count in raw_docs:
        tf = normalized_tf(counts, word_count)
        docs[name] = Document(
            name=name,
            raw_tf=counts,
            word_count=word_count,
            tf=tf,
            tfidf=tfidf_map(tf, idf),
        )
    return Index(n=n, variant=variant, df=df, idf=idf, docs=docs, members=members)


def load_committed_index(
    output_dir: Path | None = None,
    *,
    variant: str = "classic",
) -> Index:
    """Load gold TF / IDF / TF-IDF tables. N is inferred from hapax IDF for classic."""
    output_dir = output_dir or (ROOT / "output")
    idf = tables.load_tf_tsv(output_dir / "idf.txt")
    df = tables.load_df_tsv(output_dir / "df.txt")
    tf_dir = output_dir / "tf"
    tfidf_dir = output_dir / "tfidf"
    docs: dict[str, Document] = {}
    for path in tables.list_table_files(tf_dir):
        tf = tables.load_tf_tsv(path)
        word_count = infer_word_count(tf)
        raw = raw_tf_from_normalized(tf, word_count)
        tfidf_path = tfidf_dir / path.name
        tfidf = tables.load_tf_tsv(tfidf_path) if tfidf_path.exists() else tfidf_map(tf, idf)
        docs[path.name] = Document(
            name=path.name,
            raw_tf=raw,
            word_count=word_count,
            tf=tf,
            tfidf=tfidf,
        )
    n = 18
    if variant == "classic" and idf:
        hapax = max(idf.values())
        n = max(1, round(math.exp(hapax)))
    if variant not in ("classic",):
        idf = idf_map(df, n, variant="bm25-idf" if variant == "bm25" else variant)
        for doc in docs.values():
            doc.tfidf = tfidf_map(doc.tf, idf)
    members: dict[str, list[str]] = {term: [] for term in df}
    for name, doc in docs.items():
        for term in doc.raw_tf:
            if term in members:
                members[term].append(name)
    return Index(n=n, variant=variant, df=df, idf=idf, docs=docs, members=members)


def write_index_tables(index: Index, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    tf_dir = output_dir / "tf"
    tfidf_dir = output_dir / "tfidf"
    tables.write_tf_tsv(output_dir / "idf.txt", index.idf)
    tables.write_df_tsv(output_dir / "df.txt", index.df, index.members)
    for name, doc in index.docs.items():
        tables.write_tf_tsv(tf_dir / name, doc.tf)
        tables.write_tf_tsv(tfidf_dir / name, doc.tfidf)
