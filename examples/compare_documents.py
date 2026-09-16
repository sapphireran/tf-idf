#!/usr/bin/env python3
"""Compare high tf-idf terms in two precomputed tables.

Prints three ranked lists:
  shared     terms in both top windows
  only A     high in the first file, missing from the second window
  only B     high in the second file, missing from the first window

Usage (from the repo root):
    python3 examples/compare_documents.py \\
        output/tfidf/carroll-alice.txt \\
        output/tfidf/shakespeare-macbeth.txt
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Reuse the TSV loader from top_terms without turning this directory into a package.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from top_terms import load_weights  # noqa: E402


def top_window(path: Path, n: int, min_score: float) -> list[tuple[str, float]]:
    rows = [(t, s) for t, s in load_weights(path) if s > min_score]
    rows.sort(key=lambda item: (-item[1], item[0]))
    return rows[:n]


def emit(title: str, rows: list[tuple[str, float]]) -> None:
    print()
    print(title)
    print("-" * len(title))
    if not rows:
        print("(none)")
        return
    width = max(len(term) for term, _ in rows)
    for i, (term, score) in enumerate(rows, start=1):
        print(f"{i:>3}  {term:<{width}}  {score:.12g}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file_a", type=Path)
    parser.add_argument("file_b", type=Path)
    parser.add_argument("--n", type=int, default=15, help="Window size per document")
    parser.add_argument(
        "--min",
        type=float,
        default=0.0,
        help="Ignore scores at or below this value (default 0 drops exact zeros)",
    )
    args = parser.parse_args()

    for path in (args.file_a, args.file_b):
        if not path.is_file():
            print(f"not a file: {path}", file=sys.stderr)
            return 2

    top_a = top_window(args.file_a, args.n, args.min)
    top_b = top_window(args.file_b, args.n, args.min)
    map_a = dict(top_a)
    map_b = dict(top_b)

    shared = []
    for term, score_a in top_a:
        if term in map_b:
            shared.append((term, score_a, map_b[term]))

    only_a = [(t, s) for t, s in top_a if t not in map_b]
    only_b = [(t, s) for t, s in top_b if t not in map_a]

    print(f"A: {args.file_a}  (top {len(top_a)} above {args.min})")
    print(f"B: {args.file_b}  (top {len(top_b)} above {args.min})")

    print()
    print("shared in both windows")
    print("----------------------")
    if not shared:
        print("(none)")
    else:
        print(f"{'term':<16} {'score A':>14}  {'score B':>14}")
        for term, score_a, score_b in shared:
            print(f"{term:<16} {score_a:14.12g}  {score_b:14.12g}")

    emit(f"only in A  ({args.file_a.name})", only_a)
    emit(f"only in B  ({args.file_b.name})", only_b)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
