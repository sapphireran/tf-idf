#!/usr/bin/env python3
"""Cosine similarity between tf*idf tables.

    python3 examples/python/similar_docs.py \\
        --table-dir examples/tiny-corpus/output/tfidf

    python3 examples/python/similar_docs.py \\
        --tables output/tfidf/austen-emma.txt output/tfidf/austen-sense.txt

See docs/document-vectors-and-similarity.md for the geometry.
"""

from __future__ import annotations

import argparse
import math
import sys
from itertools import combinations
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from tfidf_toy import load_weight_table


def l2_norm(weights: dict[str, float]) -> float:
    return math.sqrt(sum(value * value for value in weights.values()))


def cosine(left: dict[str, float], right: dict[str, float]) -> float:
    if not left or not right:
        return 0.0
    # Only shared keys can contribute; missing = 0.
    if len(left) > len(right):
        left, right = right, left
    dot = sum(weight * right[token] for token, weight in left.items() if token in right)
    denom = l2_norm(left) * l2_norm(right)
    if denom == 0:
        return 0.0
    return dot / denom


def load_named_tables(paths: list[Path]) -> dict[str, dict[str, float]]:
    tables: dict[str, dict[str, float]] = {}
    for path in paths:
        tables[path.name] = load_weight_table(path)
    return tables


def pairwise_cosine(tables: dict[str, dict[str, float]]) -> list[tuple[str, str, float]]:
    pairs: list[tuple[str, str, float]] = []
    for left_name, right_name in combinations(sorted(tables), 2):
        score = cosine(tables[left_name], tables[right_name])
        pairs.append((left_name, right_name, score))
    pairs.sort(key=lambda row: (-row[2], row[0], row[1]))
    return pairs


def format_matrix(tables: dict[str, dict[str, float]]) -> str:
    names = sorted(tables)
    width = max(len(name) for name in names)
    # Short labels for the header so a 4-document corpus stays readable.
    header = " " * width + "".join(f"  {name[:6]:>8s}" for name in names)
    rows = [header]
    pair_scores = {(a, b): s for a, b, s in pairwise_cosine(tables)}
    for row_name in names:
        cells = []
        for col_name in names:
            if row_name == col_name:
                cells.append(f"{1.0:8.4f}")
            else:
                key = (row_name, col_name) if row_name < col_name else (col_name, row_name)
                cells.append(f"{pair_scores[key]:8.4f}")
        rows.append(f"{row_name:<{width}}" + "".join(f"  {cell}" for cell in cells))
    return "\n".join(rows)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cosine similarity of tf*idf tables.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--table-dir", type=Path, help="directory of token<TAB>weight files")
    source.add_argument("--tables", type=Path, nargs="+", help="two or more table files")
    parser.add_argument("--top-pairs", type=int, default=0, help="print only the N closest pairs (0 = all)")
    parser.add_argument("--matrix", action="store_true", help="also print a full pairwise matrix")
    return parser.parse_args(argv)


def _collect_paths(args: argparse.Namespace) -> list[Path]:
    if args.tables:
        return list(args.tables)
    directory = args.table_dir
    return sorted(p for p in directory.iterdir() if p.is_file() and not p.name.startswith("."))


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    paths = _collect_paths(args)
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        print("error: missing table(s): " + ", ".join(missing), file=sys.stderr)
        return 2
    if len(paths) < 2:
        print("error: need at least two tables to compare", file=sys.stderr)
        return 2

    tables = load_named_tables(paths)
    pairs = pairwise_cosine(tables)
    if args.top_pairs > 0:
        pairs = pairs[: args.top_pairs]

    print("# cosine similarity (highest first)")
    for left, right, score in pairs:
        print(f"  {score:.8f}  {left}  ×  {right}")

    if args.matrix:
        print()
        print(format_matrix(tables))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
