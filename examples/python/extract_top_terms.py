#!/usr/bin/env python3
"""Rank a tab-separated term<TAB>score file from this repo's output/ tree.

The Perl scripts write TF and TF-IDF tables in alphabetical term order.
This helper is the missing "sort by score" step.

    python3 examples/python/extract_top_terms.py output/tfidf/carroll-alice.txt
    python3 examples/python/extract_top_terms.py --tf output/tf/carroll-alice.txt -n 15
    python3 examples/python/extract_top_terms.py --zeros output/tfidf/carroll-alice.txt
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def load_scores(path: Path) -> list[tuple[str, float]]:
    rows: list[tuple[str, float]] = []
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line_no, raw in enumerate(handle, start=1):
            line = raw.rstrip("\n")
            if not line:
                continue
            # skip the df.txt header if someone points us at it
            if line_no == 1 and line.startswith("word"):
                continue
            term, sep, rest = line.partition("\t")
            if not sep:
                print(f"{path}:{line_no}: no tab, skipped", file=sys.stderr)
                continue
            score_field = rest.split("\t", 1)[0].strip()
            try:
                score = float(score_field)
            except ValueError:
                print(f"{path}:{line_no}: not a float: {score_field!r}", file=sys.stderr)
                continue
            rows.append((term, score))
    return rows


def format_row(rank: int, term: str, score: float) -> str:
    return f"{rank:4d}  {score: .8g}  {term}"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="TSV file (output/tf/* or output/tfidf/*)")
    parser.add_argument("-n", "--limit", type=int, default=20, help="rows to print (default 20)")
    parser.add_argument(
        "--tf",
        action="store_true",
        help="label the output as term frequency (cosmetic only)",
    )
    parser.add_argument(
        "--zeros",
        action="store_true",
        help="print how many rows are exactly 0.0, then the usual ranking",
    )
    parser.add_argument(
        "--bottom",
        action="store_true",
        help="print the lowest scores instead of the highest",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.path.is_file():
        print(f"not a file: {args.path}", file=sys.stderr)
        return 2
    rows = load_scores(args.path)
    if not rows:
        print(f"no scored rows in {args.path}", file=sys.stderr)
        return 1

    kind = "tf" if args.tf else "score"
    if args.zeros:
        n_zero = sum(1 for _, score in rows if score == 0.0)
        print(f"{args.path}: {len(rows)} terms, {n_zero} with {kind}=0")

    if args.bottom:
        rows.sort(key=lambda item: (item[1], item[0]))
    else:
        rows.sort(key=lambda item: (-item[1], item[0]))
    limit = max(args.limit, 0)
    shown = rows[:limit] if limit else rows
    print(f"# {args.path}  ranked by {kind} ({'lowest' if args.bottom else 'highest'} {len(shown)})")
    for rank, (term, score) in enumerate(shown, start=1):
        print(format_row(rank, term, score))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
