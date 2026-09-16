"""Personal reference implementation of the tf-idf pipeline in this repo.

This module is documentation you can run. It has two goals:

1. Reproduce the *intended* scoring used by the committed Gutenberg outputs:
   lowercase tokens, drop punctuation, TF as a within-document proportion,
   IDF as the natural log of N / df, and TF-IDF as the product of those two.
2. Show a few neighboring textbook variants so the formulas are easy to
   compare on a tiny corpus.

The original Perl scripts remain the historical implementation. Read
``docs/04-this-repo-pipeline.md`` for a line-by-line map onto
``tf-idf-values.pl`` and ``tf*idf-product.pl``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import log, sqrt
from pathlib import Path
import re
from typing import Iterable, Mapping


Token = str
DocName = str


_NON_ALNUM = re.compile(r"[^a-zA-Z0-9\s]")
_WHITESPACE = re.compile(r"\s+")


def tokenize(text: str, *, count_empty_like_perl: bool = False) -> list[Token]:
    """Tokenize a document the way the Perl scripts do, with one cleanup.

    Perl steps mirrored here:

    * collapse horizontal/vertical whitespace to a single space
    * lowercase ASCII letters
    * drop characters that are not letters, digits, or whitespace
    * split on one or more spaces

    The Perl loop increments the document length for empty split pieces
    (leading spaces after cleanup). That is almost never useful, so the
    default path drops empty tokens and does not count them. Pass
    ``count_empty_like_perl=True`` only when you are auditing the original
    scripts against messy input.
    """

    collapsed = _WHITESPACE.sub(" ", text)
    lowered = collapsed.lower()
    stripped = _NON_ALNUM.sub("", lowered)
    pieces = re.split(r" +", stripped)
    if count_empty_like_perl:
        return pieces
    return [piece for piece in pieces if piece]


@dataclass(frozen=True)
class Document:
    """One named bag of tokens plus the original text."""

    name: DocName
    text: str
    tokens: list[Token]

    @classmethod
    def from_text(cls, name: DocName, text: str) -> "Document":
        return cls(name=name, text=text, tokens=tokenize(text))

    @classmethod
    def from_path(cls, path: Path) -> "Document":
        return cls.from_text(path.name, path.read_text(encoding="utf-8"))

    @property
    def length(self) -> int:
        return len(self.tokens)

    def term_counts(self) -> dict[Token, int]:
        counts: dict[Token, int] = {}
        for token in self.tokens:
            counts[token] = counts.get(token, 0) + 1
        return counts


@dataclass
class TermStats:
    """Per-term collection statistics."""

    term: Token
    df: int
    idf: float
    documents: tuple[DocName, ...]


@dataclass
class ScoredDocument:
    """TF and TF-IDF vectors for one document."""

    document: Document
    tf: dict[Token, float]
    tfidf: dict[Token, float]

    def top_terms(self, n: int = 10) -> list[tuple[Token, float]]:
        ranked = sorted(self.tfidf.items(), key=lambda item: (-item[1], item[0]))
        return ranked[:n]


@dataclass
class Index:
    """A scored collection of documents."""

    documents: list[Document]
    stats: dict[Token, TermStats]
    scored: dict[DocName, ScoredDocument]
    n_documents: int
    variant: str = "repo"

    def vocabulary(self) -> list[Token]:
        return sorted(self.stats)

    def vector(self, name: DocName) -> dict[Token, float]:
        return self.scored[name].tfidf

    def cosine(self, left: DocName, right: DocName) -> float:
        return cosine_similarity(self.vector(left), self.vector(right))

    def pairwise_cosine(self) -> dict[tuple[DocName, DocName], float]:
        names = [document.name for document in self.documents]
        pairs: dict[tuple[DocName, DocName], float] = {}
        for i, left in enumerate(names):
            for right in names[i:]:
                pairs[(left, right)] = self.cosine(left, right)
        return pairs


def natural_idf(n_documents: int, df: int, *, smooth: bool = False) -> float:
    """IDF used by this repo: ``ln(N / df)``.

    The optional ``smooth`` flag is *not* what the Perl scripts do. It is
    the common ``ln((N + 1) / (df + 1)) + 1`` textbook variant, useful
    when a query term is missing from the collection.
    """

    if df <= 0:
        raise ValueError("df must be positive for unsmoothed IDF")
    if n_documents <= 0:
        raise ValueError("N must be positive")
    if smooth:
        return log((n_documents + 1) / (df + 1)) + 1.0
    return log(n_documents / df)


def tf_proportion(count: int, length: int) -> float:
    if length <= 0:
        raise ValueError("document length must be positive")
    return count / length


def tf_log_normalized(count: int) -> float:
    """A common alternative: ``1 + ln(count)`` for present terms."""

    if count <= 0:
        return 0.0
    return 1.0 + log(count)


def cosine_similarity(
    left: Mapping[Token, float], right: Mapping[Token, float]
) -> float:
    if left is right:
        return 1.0
    shared = set(left) & set(right)
    dot = sum(left[term] * right[term] for term in shared)
    left_norm = sqrt(sum(value * value for value in left.values()))
    right_norm = sqrt(sum(value * value for value in right.values()))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return dot / (left_norm * right_norm)


def load_documents(directory: Path) -> list[Document]:
    paths = sorted(
        path
        for path in directory.iterdir()
        if path.is_file() and not path.name.startswith(".")
    )
    if not paths:
        raise FileNotFoundError(f"no documents in {directory}")
    return [Document.from_path(path) for path in paths]


def build_index(
    documents: Iterable[Document],
    *,
    variant: str = "repo",
    n_override: int | None = None,
) -> Index:
    """Score a collection.

    Variants:

    * ``repo`` — TF as a proportion, IDF as ``ln(N / df)``, product TF-IDF.
      This matches the committed Gutenberg ``output/`` tables when
      ``N`` is the number of processed books (18).
    * ``log_tf`` — same IDF, but TF is ``1 + ln(count)``.
    * ``smooth_idf`` — proportion TF with smoothed IDF.
    """

    docs = list(documents)
    if not docs:
        raise ValueError("need at least one document")

    names = [doc.name for doc in docs]
    if len(set(names)) != len(names):
        raise ValueError("document names must be unique")

    df_map: dict[Token, set[DocName]] = {}
    counts: dict[DocName, dict[Token, int]] = {}
    for doc in docs:
        term_counts = doc.term_counts()
        counts[doc.name] = term_counts
        for term in term_counts:
            df_map.setdefault(term, set()).add(doc.name)

    n_documents = n_override if n_override is not None else len(docs)
    smooth = variant == "smooth_idf"
    stats: dict[Token, TermStats] = {}
    for term, owners in df_map.items():
        df = len(owners)
        stats[term] = TermStats(
            term=term,
            df=df,
            idf=natural_idf(n_documents, df, smooth=smooth),
            documents=tuple(sorted(owners)),
        )

    scored: dict[DocName, ScoredDocument] = {}
    for doc in docs:
        tf: dict[Token, float] = {}
        tfidf: dict[Token, float] = {}
        for term, count in counts[doc.name].items():
            if variant == "log_tf":
                tf_value = tf_log_normalized(count)
            else:
                tf_value = tf_proportion(count, doc.length)
            tf[term] = tf_value
            tfidf[term] = tf_value * stats[term].idf
        scored[doc.name] = ScoredDocument(document=doc, tf=tf, tfidf=tfidf)

    return Index(
        documents=docs,
        stats=stats,
        scored=scored,
        n_documents=n_documents,
        variant=variant,
    )


def write_tsv(path: Path, rows: Iterable[tuple[str, float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"{key}\t{value}" for key, value in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_index(index: Index, output_dir: Path) -> None:
    """Write TF, IDF, DF, and TF-IDF tables in the same TSV shape as ``output/``."""

    tf_dir = output_dir / "tf"
    tfidf_dir = output_dir / "tfidf"
    tf_dir.mkdir(parents=True, exist_ok=True)
    tfidf_dir.mkdir(parents=True, exist_ok=True)

    idf_rows = [(term, index.stats[term].idf) for term in index.vocabulary()]
    write_tsv(output_dir / "idf.txt", idf_rows)

    df_lines = ["word\t#docs it exists in\tdoc names"]
    for term in index.vocabulary():
        stat = index.stats[term]
        owners = ", ".join(stat.documents)
        df_lines.append(f"{term}\t{stat.df}\t{owners}")
    (output_dir / "df.txt").write_text("\n".join(df_lines) + "\n", encoding="utf-8")

    for name, scored in index.scored.items():
        write_tsv(tf_dir / name, sorted(scored.tf.items()))
        write_tsv(tfidf_dir / name, sorted(scored.tfidf.items()))


def read_term_weights(path: Path) -> dict[Token, float]:
    weights: dict[Token, float] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw or raw.startswith("word"):
            continue
        term, value, *_ = raw.split("\t")
        try:
            weights[term] = float(value)
        except ValueError:
            continue
    return weights


def top_terms_from_weights(
    weights: Mapping[Token, float], n: int = 15
) -> list[tuple[Token, float]]:
    return sorted(weights.items(), key=lambda item: (-item[1], item[0]))[:n]


@dataclass
class WorkedRow:
    """One hand-checkable cell in the three-sentence toy example."""

    term: Token
    document: DocName
    count: int
    length: int
    tf: float
    df: int
    idf: float
    tfidf: float


@dataclass
class WorkedExample:
    """The fully expanded 3-document classroom example."""

    documents: list[Document] = field(default_factory=list)
    index: Index | None = None
    rows: list[WorkedRow] = field(default_factory=list)


WORKED_TEXTS = {
    "mats.txt": "cats sit on mats",
    "logs.txt": "dogs sit on logs",
    "chase.txt": "cats chase dogs",
}


def build_worked_example() -> WorkedExample:
    documents = [
        Document.from_text(name, text) for name, text in WORKED_TEXTS.items()
    ]
    index = build_index(documents, variant="repo")
    rows: list[WorkedRow] = []
    for doc in documents:
        counts = doc.term_counts()
        for term in sorted(counts):
            count = counts[term]
            stat = index.stats[term]
            tf = tf_proportion(count, doc.length)
            rows.append(
                WorkedRow(
                    term=term,
                    document=doc.name,
                    count=count,
                    length=doc.length,
                    tf=tf,
                    df=stat.df,
                    idf=stat.idf,
                    tfidf=tf * stat.idf,
                )
            )
    return WorkedExample(documents=documents, index=index, rows=rows)
