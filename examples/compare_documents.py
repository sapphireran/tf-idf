#!/usr/bin/env python3
"""Cosine similarity over the checked-in per-book TF-IDF tables.

Each output/tfidf/<book>.txt becomes a sparse vector. Terms that never
appear in a book are implicit zeros. Collection-wide words (IDF 0) sit in
the files as zeros and do not affect the dot product.

Run from the repository root:

    python3 examples/compare_documents.py --a carroll-alice --b austen-emma
    python3 examples/compare_documents.py --matrix
    python3 examples/compare_documents.py --a austen-emma --b austen-sense --show-overlap 15
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TFIDF_DIR = REPO_ROOT / "output" / "tfidf"


def load_vector(path: Path) -> dict[str, float]:
    vector: dict[str, float] = {}
    with path.open(encoding="utf-8", errors="replace") as handle:
        for raw in handle:
            line = raw.rstrip("\n")
            if not line:
                continue
            term, sep, rest = line.partition("\t")
            if not sep:
                continue
            try:
                value = float(rest.split("\t", 1)[0])
            except ValueError:
                continue
            if value != 0.0:
                vector[term] = value
    return vector


def normalize_doc_name(name: str) -> str:
    name = name.strip()
    if not name.endswith(".txt"):
        name += ".txt"
    return name


def short_name(name: str) -> str:
    return name.removesuffix(".txt")


def available_docs() -> list[str]:
    return sorted(p.name for p in TFIDF_DIR.glob("*.txt"))


def dot(left: dict[str, float], right: dict[str, float]) -> float:
    if len(left) > len(right):
        left, right = right, left
    return sum(value * right[term] for term, value in left.items() if term in right)


def norm(vector: dict[str, float]) -> float:
    return math.sqrt(sum(value * value for value in vector.values()))


def cosine(left: dict[str, float], right: dict[str, float]) -> float:
    left_norm = norm(left)
    right_norm = norm(right)
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return dot(left, right) / (left_norm * right_norm)


def overlapping_terms(
    left: dict[str, float], right: dict[str, float]
) -> list[tuple[str, float, float, float]]:
    terms = set(left) & set(right)
    rows = []
    for term in terms:
        product = left[term] * right[term]
        rows.append((term, left[term], right[term], product))
    rows.sort(key=lambda row: (-row[3], row[0]))
    return rows


def load_named(name: str, cache: dict[str, dict[str, float]]) -> dict[str, float]:
    if name not in cache:
        cache[name] = load_vector(TFIDF_DIR / name)
    return cache[name]


def print_pair(
    left_name: str,
    right_name: str,
    cache: dict[str, dict[str, float]],
    overlap_n: int,
) -> None:
    left = load_named(left_name, cache)
    right = load_named(right_name, cache)
    score = cosine(left, right)
    shared = set(left) & set(right)
    print(f"{short_name(left_name)}  vs  {short_name(right_name)}")
    print(f"  cosine          {score:.6f}")
    print(f"  |left| / |right| {len(left)} / {len(right)}")
    print(f"  shared nonzero  {len(shared)}")
    if overlap_n > 0 and shared:
        print(f"  top overlap by product (n={overlap_n}):")
        for term, lv, rv, product in overlapping_terms(left, right)[:overlap_n]:
            print(f"    {term:<16}  L={lv:.6g}  R={rv:.6g}  L*R={product:.6g}")


def print_matrix(names: list[str], cache: dict[str, dict[str, float]]) -> None:
    vectors = [load_named(name, cache) for name in names]
    labels = [short_name(name)[:16] for name in names]
    width = max(16, max(len(label) for label in labels))
    header = " " * width + "  " + "  ".join(f"{label:>8.8}" for label in labels)
    print(header)
    for i, left in enumerate(vectors):
        cells = []
        for j, right in enumerate(vectors):
            cells.append(f"{cosine(left, right):8.4f}")
        print(f"{labels[i]:<{width}}  " + "  ".join(cells))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Cosine similarity between checked-in TF-IDF book vectors."
    )
    parser.add_argument("--a", help="First book (stem or filename).")
    parser.add_argument("--b", help="Second book (stem or filename).")
    parser.add_argument(
        "--matrix",
        action="store_true",
        help="Print an all-vs-all cosine matrix for every book.",
    )
    parser.add_argument(
        "--show-overlap",
        type=int,
        default=0,
        metavar="N",
        help="With --a/--b, show the N terms with the largest product.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Print available document names and exit.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not TFIDF_DIR.is_dir():
        print(f"error: missing {TFIDF_DIR}", file=sys.stderr)
        return 2

    names = available_docs()
    if args.list:
        for name in names:
            print(name)
        return 0

    if not names:
        print(f"error: no TF-IDF tables in {TFIDF_DIR}", file=sys.stderr)
        return 2

    cache: dict[str, dict[str, float]] = {}

    if args.matrix:
        print_matrix(names, cache)
        if args.a and args.b:
            print()
        else:
            return 0

    if args.a or args.b:
        if not (args.a and args.b):
            print("error: --a and --b must be given together", file=sys.stderr)
            return 2
        left = normalize_doc_name(args.a)
        right = normalize_doc_name(args.b)
        missing = [name for name in (left, right) if name not in names]
        if missing:
            print("error: unknown document(s): " + ", ".join(missing), file=sys.stderr)
            return 2
        print_pair(left, right, cache, args.show_overlap)
        return 0

    if args.matrix:
        return 0

    print("error: provide --a and --b, or --matrix, or --list", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
