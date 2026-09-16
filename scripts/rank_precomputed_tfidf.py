#!/usr/bin/env python3
"""Rank terms from the precomputed ``output/tfidf`` tables.

The 2012 Perl scripts write one TSV file per Gutenberg text, sorted
alphabetically by term. That is handy for diffs and joins, but it hides
the usual question: *which words actually distinguish this book?*

This helper reads those tables and prints the highest tf*idf scores.

    python3 scripts/rank_precomputed_tfidf.py
    python3 scripts/rank_precomputed_tfidf.py --input output/tfidf --top 12
    python3 scripts/rank_precomputed_tfidf.py --only carroll-alice.txt
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def load_scores(path: Path) -> list[tuple[str, float]]:
    rows: list[tuple[str, float]] = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not raw.strip() or "\t" not in raw:
            continue
        term, value = raw.split("\t", 1)
        try:
            score = float(value)
        except ValueError:
            continue
        rows.append((term, score))
    rows.sort(key=lambda item: (-item[1], item[0]))
    return rows


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("output/tfidf"),
        help="directory of precomputed tf*idf TSV files",
    )
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument(
        "--only",
        action="append",
        default=[],
        help="limit to one or more filenames (repeatable)",
    )
    parser.add_argument(
        "--min-length",
        type=int,
        default=0,
        help="drop terms shorter than this (useful for speaker tags)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.input.is_dir():
        sys.stderr.write(f"missing directory: {args.input}\n")
        return 1

    wanted = set(args.only)
    files = sorted(
        path
        for path in args.input.iterdir()
        if path.is_file() and not path.name.startswith(".")
    )
    if wanted:
        files = [path for path in files if path.name in wanted]
        missing = wanted - {path.name for path in files}
        if missing:
            sys.stderr.write("not found: " + ", ".join(sorted(missing)) + "\n")
            return 1

    for path in files:
        ranked = [
            (term, score)
            for term, score in load_scores(path)
            if len(term) >= args.min_length
        ][: args.top]
        print(f"=== {path.name} ===")
        if not ranked:
            print("(no terms)")
            print()
            continue
        width = max(len(term) for term, _ in ranked)
        for term, score in ranked:
            print(f"  {term.ljust(width)}  {score:.6f}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
