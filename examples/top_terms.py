#!/usr/bin/env python3
"""Print the highest-weighted terms from a term<TAB>score table.

The original Perl writers emit files in alphabetical term order. This
helper is the supported way to read a ranking. It uses ordinary float()
parsing, so scientific notation is fine.

Usage (from the repo root):
    python3 examples/top_terms.py output/tfidf/carroll-alice.txt
    python3 examples/top_terms.py output/tfidf/carroll-alice.txt --n 25
    python3 examples/top_terms.py output/tf/carroll-alice.txt --n 10 --min 0
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def load_weights(path: Path) -> list[tuple[str, float]]:
    rows: list[tuple[str, float]] = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.rstrip("\n\r")
        if not line or line.startswith("word \t"):
            continue
        if "\t" not in line:
            raise ValueError(f"{path}:{lineno}: expected tab-separated term and score")
        term, score = line.split("\t", 1)
        # df.txt has a third column; ignore it if someone points us there.
        score = score.split("\t", 1)[0].strip()
        if score == "":
            raise ValueError(f"{path}:{lineno}: missing score")
        rows.append((term, float(score)))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("table", type=Path, help="TSV file (output/tfidf/… or output/tf/…)")
    parser.add_argument("--n", type=int, default=15, help="How many rows to print (default 15)")
    parser.add_argument(
        "--min",
        type=float,
        default=None,
        help="Drop scores at or below this value (default: keep zeros)",
    )
    args = parser.parse_args()

    if not args.table.is_file():
        print(f"not a file: {args.table}", file=sys.stderr)
        return 2

    rows = load_weights(args.table)
    if args.min is not None:
        rows = [(t, s) for t, s in rows if s > args.min]
    rows.sort(key=lambda item: (-item[1], item[0]))
    if args.n >= 0:
        rows = rows[: args.n]

    width = max((len(term) for term, _ in rows), default=4)
    print(f"# {args.table}  ({len(rows)} shown)")
    print(f"{'rank':>4}  {'term':<{width}}  score")
    for i, (term, score) in enumerate(rows, start=1):
        print(f"{i:>4}  {term:<{width}}  {score:.12g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
