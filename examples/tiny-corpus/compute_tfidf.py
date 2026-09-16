#!/usr/bin/env python3
"""TF-IDF for the four-document teaching corpus.

Tokenizer matches the personal Perl scripts:

    lowercase, delete [^a-zA-Z0-9 whitespace], split on spaces

Document count N is the number of non-hidden files in docs/, not a
readdir last-index. Empty tokens are ignored and do *not* inflate the
denominator (the one intentional difference from tf-idf-values.pl).

Run from the repository root or from this directory:

    python3 examples/tiny-corpus/compute_tfidf.py
    python3 examples/tiny-corpus/compute_tfidf.py --show-tokens
    python3 examples/tiny-corpus/compute_tfidf.py --json
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
DOCS_DIR = HERE / "docs"
TOKEN_KEEP = re.compile(r"[^a-zA-Z0-9\s]+")


def tokenize(text: str) -> list[str]:
    # Match the Perl pass-1 cleanup: collapse any whitespace (the Perl
    # [\h\v]+ class), lowercase, drop punctuation, split on spaces.
    text = re.sub(r"\s+", " ", text)
    text = text.lower()
    text = TOKEN_KEEP.sub("", text)
    text = text.strip()
    return [tok for tok in text.split(" ") if tok]


@dataclass
class Document:
    name: str
    raw: str
    tokens: list[str]
    tf: dict[str, float] = field(default_factory=dict)

    @property
    def n_tokens(self) -> int:
        return len(self.tokens)


def load_documents(docs_dir: Path) -> list[Document]:
    paths = sorted(
        path for path in docs_dir.iterdir() if path.is_file() and not path.name.startswith(".")
    )
    documents: list[Document] = []
    for path in paths:
        raw = path.read_text(encoding="utf-8")
        tokens = tokenize(raw)
        counts: dict[str, int] = {}
        for token in tokens:
            counts[token] = counts.get(token, 0) + 1
        n_tokens = len(tokens)
        tf = {term: count / n_tokens for term, count in counts.items()} if n_tokens else {}
        documents.append(Document(name=path.name, raw=raw, tokens=tokens, tf=tf))
    return documents


def document_frequency(documents: list[Document]) -> dict[str, int]:
    df: dict[str, int] = {}
    for doc in documents:
        for term in doc.tf:
            df[term] = df.get(term, 0) + 1
    return df


def inverse_document_frequency(df: dict[str, int], n_docs: int) -> dict[str, float]:
    return {term: math.log(n_docs / count) for term, count in df.items()}


def tfidf_table(
    documents: list[Document], idf: dict[str, float]
) -> dict[str, dict[str, float]]:
    table: dict[str, dict[str, float]] = {}
    for doc in documents:
        table[doc.name] = {term: tf * idf[term] for term, tf in doc.tf.items()}
    return table


def print_human(
    documents: list[Document],
    df: dict[str, int],
    idf: dict[str, float],
    tfidf: dict[str, dict[str, float]],
    show_tokens: bool,
) -> None:
    n_docs = len(documents)
    print(f"N = {n_docs} documents")
    print(f"vocabulary = {len(df)} terms")
    print(f"idf(t) = ln(N / df(t))")
    print()

    for doc in documents:
        print(f"## {doc.name}  ({doc.n_tokens} tokens)")
        if show_tokens:
            print(f"   tokens: {doc.tokens}")
        print(f"{'term':<12} {'count':>7} {'tf':>10} {'df':>4} {'idf':>10} {'tfidf':>10}")
        rows = []
        counts: dict[str, int] = {}
        for token in doc.tokens:
            counts[token] = counts.get(token, 0) + 1
        for term in sorted(doc.tf, key=lambda t: (-tfidf[doc.name][t], t)):
            rows.append(
                (
                    term,
                    counts[term],
                    doc.tf[term],
                    df[term],
                    idf[term],
                    tfidf[doc.name][term],
                )
            )
        for term, count, tf, dfi, idfv, score in rows:
            print(
                f"{term:<12} {count:7d} {tf:10.6f} {dfi:4d} {idfv:10.6f} {score:10.6f}"
            )
        print()

    print("## collection IDF")
    print(f"{'term':<12} {'df':>4} {'idf':>10}")
    for term in sorted(idf, key=lambda t: (-idf[t], t)):
        print(f"{term:<12} {df[term]:4d} {idf[term]:10.6f}")


def as_json(
    documents: list[Document],
    df: dict[str, int],
    idf: dict[str, float],
    tfidf: dict[str, dict[str, float]],
) -> dict:
    return {
        "n_docs": len(documents),
        "formula": {"tf": "count / tokens", "idf": "ln(N / df)", "tfidf": "tf * idf"},
        "documents": {
            doc.name: {
                "n_tokens": doc.n_tokens,
                "tokens": doc.tokens,
                "tf": doc.tf,
                "tfidf": tfidf[doc.name],
            }
            for doc in documents
        },
        "df": df,
        "idf": idf,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compute TF-IDF on the tiny teaching corpus.")
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=DOCS_DIR,
        help="Directory of documents (default: ./docs next to this script).",
    )
    parser.add_argument("--show-tokens", action="store_true")
    parser.add_argument("--json", action="store_true", help="Dump the tables as JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    docs_dir = args.docs_dir
    if not docs_dir.is_dir():
        print(f"error: missing {docs_dir}", file=sys.stderr)
        return 2
    documents = load_documents(docs_dir)
    if not documents:
        print(f"error: no documents in {docs_dir}", file=sys.stderr)
        return 2
    df = document_frequency(documents)
    idf = inverse_document_frequency(df, len(documents))
    tfidf = tfidf_table(documents, idf)
    if args.json:
        json.dump(as_json(documents, df, idf, tfidf), sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    else:
        print_human(documents, df, idf, tfidf, args.show_tokens)
    return 0


if __name__ == "__main__":
    sys.exit(main())
