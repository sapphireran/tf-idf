#!/usr/bin/env python3
"""Pairwise cosine similarity, plus an optional ad-hoc query."""

from __future__ import annotations

import argparse
from pathlib import Path

import _paths  # noqa: F401
from tfidfkit.similarity import cosine, query_vector, rank_neighbors
from tfidfkit.tables import read_idf, read_weighted_dir


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tfidf-dir", type=Path, required=True)
    parser.add_argument("--top", type=int, default=15)
    parser.add_argument(
        "--mode",
        choices=("tfidf", "boolean"),
        default="tfidf",
        help="tfidf uses stored weights; boolean uses presence of non-zero weight",
    )
    parser.add_argument("--query", help="Score a free-text query against every document")
    parser.add_argument(
        "--idf",
        type=Path,
        help="idf.txt used when --query is set (defaults to sibling ../idf.txt)",
    )
    parser.add_argument("--neighbors-of", help="Print only pairs that include this filename")
    args = parser.parse_args()

    documents = read_weighted_dir(args.tfidf_dir)

    if args.query:
        idf_path = args.idf
        if idf_path is None:
            idf_path = args.tfidf_dir.parent / "idf.txt"
        idf, dirty = read_idf(idf_path)
        if dirty:
            print(f"# warning: dirty idf rows: {', '.join(dirty)}")
        qv = query_vector(args.query, idf)
        ranked = sorted(
            ((name, cosine(qv, weights)) for name, weights in documents.items()),
            key=lambda item: (-item[1], item[0]),
        )
        print(f"# query\t{args.query}")
        for rank, (name, score) in enumerate(ranked[: args.top], start=1):
            print(f"{rank:>4}\t{name}\t{score:.8f}")
        return 0

    pairs = rank_neighbors(documents, mode=args.mode)
    if args.neighbors_of:
        pairs = [
            row
            for row in pairs
            if args.neighbors_of in (row[0], row[1])
        ]
    print(f"# mode={args.mode} pairs={len(pairs)}")
    for left, right, score in pairs[: args.top]:
        print(f"{left}\t{right}\t{score:.8f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
