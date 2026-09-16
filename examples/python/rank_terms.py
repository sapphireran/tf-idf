#!/usr/bin/env python3
"""Rank tokens in a committed or freshly written tf / tfidf table.

The 2012 Perl writers store rows in alphabetical token order. This script
is the missing “sort by weight” step.

    python3 examples/python/rank_terms.py \\
        --from-table output/tfidf/carroll-alice.txt --top 15

    python3 examples/python/rank_terms.py \\
        --from-dir output/tfidf --top 5
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from tfidf_toy import load_weight_table, ranked_terms


def _print_ranking(title: str, path: Path, top: int) -> None:
    weights = load_weight_table(path)
    print(f"# {title}  (vocab={len(weights)})")
    for rank, (token, weight) in enumerate(ranked_terms(weights, top=top), start=1):
        print(f"  {rank:3d}  {token:20s} {weight:.8g}")
    print()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rank tokens in tf or tf*idf TSV files.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--from-table", type=Path, help="one token<TAB>weight file")
    source.add_argument("--from-dir", type=Path, help="directory of those files")
    parser.add_argument("--top", type=int, default=12, help="how many rows to print")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.top < 1:
        print("error: --top must be >= 1", file=sys.stderr)
        return 2
    if args.from_table:
        if not args.from_table.is_file():
            print(f"error: not a file: {args.from_table}", file=sys.stderr)
            return 2
        _print_ranking(args.from_table.name, args.from_table, args.top)
        return 0

    directory = args.from_dir
    if not directory.is_dir():
        print(f"error: not a directory: {directory}", file=sys.stderr)
        return 2
    files = sorted(p for p in directory.iterdir() if p.is_file() and not p.name.startswith("."))
    if not files:
        print(f"error: no tables in {directory}", file=sys.stderr)
        return 2
    for path in files:
        _print_ranking(path.name, path, args.top)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
