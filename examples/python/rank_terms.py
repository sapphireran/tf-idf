#!/usr/bin/env python3
"""Rank tokens in one document, or emit a top-N table for every document."""

from __future__ import annotations

import argparse
from pathlib import Path

import _paths  # noqa: F401
from tfidfkit.tables import iter_ranked, load_committed, read_weighted_dir


def _is_digit_token(token: str) -> bool:
    return token.isdigit()


def _format_row(rank: int, token: str, weight: float) -> str:
    return f"{rank:>4}\t{token}\t{weight:.8g}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tfidf-dir", type=Path, required=True)
    parser.add_argument(
        "--document",
        help="Filename inside --tfidf-dir. Omit to print every document.",
    )
    parser.add_argument("--top", type=int, default=15)
    parser.add_argument(
        "--drop-digits",
        action="store_true",
        help="Hide tokens that are only digits (verse numbers, years)",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        help="If set, also load df/idf from this snapshot root for extra columns",
    )
    args = parser.parse_args()

    tables = read_weighted_dir(args.tfidf_dir)
    df_map = {}
    idf_map = {}
    if args.output_root is not None:
        committed = load_committed(args.output_root)
        df_map = committed.df
        idf_map = committed.idf

    names = [args.document] if args.document else sorted(tables)
    for name in names:
        if name not in tables:
            raise SystemExit(f"unknown document: {name}")
        print(f"# {name}")
        ranked = [
            (token, weight)
            for token, weight in iter_ranked(tables[name])
            if not (args.drop_digits and _is_digit_token(token))
        ]
        for rank, (token, weight) in enumerate(ranked[: args.top], start=1):
            extra = ""
            if token in df_map:
                extra = f"\tdf={df_map[token][0]}\tidf={idf_map.get(token, float('nan')):.6g}"
            print(_format_row(rank, token, weight) + extra)
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
