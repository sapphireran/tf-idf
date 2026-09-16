#!/usr/bin/env python3
"""A small, dependency-free TF-IDF toy for this personal repo.

The original 2012 Perl scripts in the repository root scan Project
Gutenberg files, write a term-frequency table per document, a corpus
document-frequency table, an inverse-document-frequency table, and a
tf*idf table per document.

This module does the same math on a folder of tiny UTF-8 texts so the
pipeline is easy to inspect, test, and walk through by hand:

    normalized_tf(term, doc) = count(term, doc) / |doc|
    idf(term)                = ln(N / df(term))
    tfidf(term, doc)         = normalized_tf(term, doc) * idf(term)

N is the number of documents that actually contain tokens, not the
last index of a ``readdir`` array. Words that appear in every document
get idf = 0, so they disappear from rankings even if they are frequent.

Run from the repository root:

    python3 examples/tfidf_toy.py --corpus examples/tiny-corpus --top 8
    python3 examples/tfidf_toy.py --corpus examples/classic-three-docs
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


Token = str
DocName = str
ScoreMap = dict[Token, float]


_NON_ALNUM = re.compile(r"[^a-z0-9\s]")
_WHITESPACE = re.compile(r"\s+")


def tokenize(text: str) -> list[Token]:
    """Mirror the original Perl tokenizer closely enough for teaching.

    ``tf-idf-values.pl`` lowercases, strips characters outside
    ``[A-Za-z0-9]`` plus whitespace, and splits on spaces. Apostrophes
    therefore vanish (``alice's`` becomes ``alices``), and digits are
    kept (verse numbers in the King James Bible become vocabulary).
    """

    collapsed = _WHITESPACE.sub(" ", text).strip().lower()
    stripped = _NON_ALNUM.sub("", collapsed)
    return [token for token in stripped.split(" ") if token]


def normalized_tf(tokens: Iterable[Token]) -> ScoreMap:
    """Return count(term) / len(tokens). Empty documents yield {}."""

    token_list = list(tokens)
    if not token_list:
        return {}
    counts = Counter(token_list)
    n = len(token_list)
    return {term: count / n for term, count in counts.items()}


def document_frequency(tf_tables: dict[DocName, ScoreMap]) -> dict[Token, int]:
    """How many documents contain each term at least once."""

    df: dict[Token, int] = defaultdict(int)
    for tf in tf_tables.values():
        for term in tf:
            df[term] += 1
    return dict(df)


def inverse_document_frequency(
    df: dict[Token, int], n_docs: int
) -> ScoreMap:
    """Natural-log IDF with no smoothing: ln(N / df).

    This matches ``log($n/($#vals+1))`` in the original Perl, using
    Perl's ``log`` (natural logarithm). Callers must pass the true
    document count as ``n_docs``.
    """

    if n_docs <= 0:
        raise ValueError("n_docs must be positive")
    idf: ScoreMap = {}
    for term, seen_in in df.items():
        if seen_in <= 0:
            raise ValueError(f"non-positive df for {term!r}")
        if seen_in > n_docs:
            raise ValueError(f"df({term})={seen_in} exceeds N={n_docs}")
        idf[term] = math.log(n_docs / seen_in)
    return idf


def tfidf_product(tf: ScoreMap, idf: ScoreMap) -> ScoreMap:
    """Pointwise product. Missing IDF values are treated as 0."""

    return {term: tf[term] * idf.get(term, 0.0) for term in tf}


def top_k(scores: ScoreMap, k: int) -> list[tuple[Token, float]]:
    """Highest scores first; break ties with the term string."""

    ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    if k < 0:
        return ranked
    return ranked[:k]


def load_corpus(corpus_dir: Path) -> dict[DocName, str]:
    """Read ``*.txt`` files, skipping names that start with a dot."""

    if not corpus_dir.is_dir():
        raise FileNotFoundError(f"corpus directory not found: {corpus_dir}")
    documents: dict[DocName, str] = {}
    for path in sorted(corpus_dir.iterdir()):
        if not path.is_file() or path.name.startswith(".") or path.suffix != ".txt":
            continue
        documents[path.name] = path.read_text(encoding="utf-8")
    if not documents:
        raise ValueError(f"no .txt files in {corpus_dir}")
    return documents


def analyze_corpus(documents: dict[DocName, str]) -> dict[str, object]:
    """Run the full pipeline. Returns tables used by the CLI and tests."""

    tokens_by_doc = {name: tokenize(text) for name, text in documents.items()}
    tf_tables = {name: normalized_tf(tokens) for name, tokens in tokens_by_doc.items()}
    n_docs = len(tf_tables)
    df = document_frequency(tf_tables)
    idf = inverse_document_frequency(df, n_docs)
    tfidf_tables = {
        name: tfidf_product(tf, idf) for name, tf in tf_tables.items()
    }
    return {
        "documents": documents,
        "tokens_by_doc": tokens_by_doc,
        "tf": tf_tables,
        "df": df,
        "idf": idf,
        "tfidf": tfidf_tables,
        "n_docs": n_docs,
    }


def write_tables(result: dict[str, object], out_dir: Path) -> None:
    """Write TSV files similar in spirit to ``output/`` in this repo."""

    out_dir.mkdir(parents=True, exist_ok=True)
    tf_dir = out_dir / "tf"
    tfidf_dir = out_dir / "tfidf"
    tf_dir.mkdir(exist_ok=True)
    tfidf_dir.mkdir(exist_ok=True)

    df: dict[Token, int] = result["df"]  # type: ignore[assignment]
    idf: ScoreMap = result["idf"]  # type: ignore[assignment]
    tf_tables: dict[DocName, ScoreMap] = result["tf"]  # type: ignore[assignment]
    tfidf_tables: dict[DocName, ScoreMap] = result["tfidf"]  # type: ignore[assignment]

    with (out_dir / "df.tsv").open("w", encoding="utf-8") as handle:
        handle.write("term\tdf\n")
        for term in sorted(df):
            handle.write(f"{term}\t{df[term]}\n")

    with (out_dir / "idf.tsv").open("w", encoding="utf-8") as handle:
        for term in sorted(idf):
            handle.write(f"{term}\t{idf[term]:.12g}\n")

    for name, tf in tf_tables.items():
        with (tf_dir / name).open("w", encoding="utf-8") as handle:
            for term in sorted(tf):
                handle.write(f"{term}\t{tf[term]:.12g}\n")

    for name, scores in tfidf_tables.items():
        with (tfidf_dir / name).open("w", encoding="utf-8") as handle:
            for term in sorted(scores):
                handle.write(f"{term}\t{scores[term]:.12g}\n")


def format_ranking(result: dict[str, object], k: int) -> str:
    """Pretty-print the top-k tf*idf terms for every document."""

    tfidf_tables: dict[DocName, ScoreMap] = result["tfidf"]  # type: ignore[assignment]
    n_docs = result["n_docs"]
    lines = [
        f"N = {n_docs} documents",
        f"vocabulary = {len(result['idf'])} terms",  # type: ignore[arg-type]
        "",
    ]
    for name in sorted(tfidf_tables):
        lines.append(f"=== {name} ===")
        ranked = top_k(tfidf_tables[name], k)
        if not ranked:
            lines.append("(empty)")
            lines.append("")
            continue
        width = max(len(term) for term, _ in ranked)
        for term, score in ranked:
            lines.append(f"  {term.ljust(width)}  {score:.6f}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--corpus",
        type=Path,
        default=Path("examples/tiny-corpus"),
        help="directory of .txt documents (default: examples/tiny-corpus)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=8,
        help="how many terms to print per document (default: 8)",
    )
    parser.add_argument(
        "--write-dir",
        type=Path,
        default=None,
        help="optional directory for TSV dumps of tf, df, idf, and tfidf",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result = analyze_corpus(load_corpus(args.corpus))
    sys.stdout.write(format_ranking(result, args.top))
    if args.write_dir is not None:
        write_tables(result, args.write_dir)
        sys.stdout.write(f"\nwrote tables under {args.write_dir}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
