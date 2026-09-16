#!/usr/bin/env python3
"""Cosine similarity between tf-idf vectors.

A document is a sparse dict of term -> tf-idf. Cosine is the usual
dot(a,b) / (|a||b|). Zeros (idf-0 stopwords) do not contribute.

Usage (from the repo root):
    python3 examples/cosine_similarity.py \\
        output/tfidf/austen-emma.txt output/tfidf/austen-sense.txt

    python3 examples/cosine_similarity.py --matrix --n 12

    python3 examples/cosine_similarity.py --toy
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tfidf_mini import analyze_directory, cosine, pairwise_cosine  # noqa: E402
from top_terms import load_weights  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TFIDF_DIR = ROOT / "output" / "tfidf"
TOY = Path(__file__).resolve().parent / "toy-corpus"


def load_vector(path: Path) -> dict[str, float]:
    return {term: score for term, score in load_weights(path) if score != 0.0}


def load_all(directory: Path) -> dict[str, dict[str, float]]:
    vectors = {}
    for path in sorted(directory.glob("*.txt")):
        vectors[path.name] = load_vector(path)
    return vectors


def print_pair(left: str, right: str, score: float) -> None:
    print(f"{score:.6f}  {left}  ×  {right}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file_a", type=Path, nargs="?")
    parser.add_argument("file_b", type=Path, nargs="?")
    parser.add_argument(
        "--matrix",
        action="store_true",
        help="Rank every pair under output/tfidf/",
    )
    parser.add_argument("--n", type=int, default=15, help="How many pairs to print")
    parser.add_argument(
        "--toy",
        action="store_true",
        help="Pairwise cosine on examples/toy-corpus",
    )
    parser.add_argument(
        "--dir",
        type=Path,
        default=TFIDF_DIR,
        help="Directory of term<TAB>score files for --matrix",
    )
    args = parser.parse_args()

    if args.toy:
        result = analyze_directory(TOY, faithful=True)
        pairs = pairwise_cosine(result["tfidf"])
        print(f"toy corpus pairwise cosine (N={result['n_docs']})")
        for left, right, score in pairs:
            print_pair(left, right, score)
        return 0

    if args.file_a and args.file_b:
        vec_a = load_vector(args.file_a)
        vec_b = load_vector(args.file_b)
        score = cosine(vec_a, vec_b)
        print(f"cosine({args.file_a.name}, {args.file_b.name}) = {score:.6f}")
        print(f"  nonzero dims: {len(vec_a)} and {len(vec_b)}")
        overlap = sorted(
            set(vec_a) & set(vec_b),
            key=lambda t: -(vec_a[t] * vec_b[t]),
        )
        print("  strongest overlapping dimensions:")
        for term in overlap[:8]:
            print(f"    {term:<16} {vec_a[term]:.6g} × {vec_b[term]:.6g}")
        return 0

    if args.matrix:
        vectors = load_all(args.dir)
        if len(vectors) < 2:
            print(f"need at least two tables in {args.dir}", file=sys.stderr)
            return 2
        pairs = pairwise_cosine(vectors)
        print(f"# pairwise cosine in {args.dir}  ({len(vectors)} docs, {len(pairs)} pairs)")
        for left, right, score in pairs[: args.n]:
            print_pair(left, right, score)
        print()
        print("lowest:")
        for left, right, score in pairs[-3:]:
            print_pair(left, right, score)
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
