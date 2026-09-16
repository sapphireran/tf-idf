#!/usr/bin/env python3
"""Rank terms in this repo's TF or TF-IDF TSV files.

The Perl scripts write terms alphabetically. A string sort on the score
column also lies once scientific notation appears. This helper parses
column 2 as a float (and tolerates the one historical `thatyou` junk
suffix in output/idf.txt).

Examples:

    python3 examples/rank_top_terms.py --dir output/tfidf --k 12
    python3 examples/rank_top_terms.py --dir output/tf --file austen-emma.txt --k 8
    python3 examples/rank_top_terms.py --dir output/tfidf --zeros
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

_JUNK_SUFFIX = re.compile(r"[^0-9eE.+-]+$")


def parse_float(raw: str) -> float:
    try:
        return float(raw)
    except ValueError:
        cleaned = _JUNK_SUFFIX.sub("", raw)
        return float(cleaned)


def load_scores(path: Path) -> list[tuple[str, float]]:
    rows: list[tuple[str, float]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line:
            continue
        if line.startswith("word \t") or line.startswith("word\t"):
            continue
        term, value = line.split("\t", 1)
        # df.txt has a third column; ignore it if someone points --dir at output/
        value = value.split("\t", 1)[0]
        rows.append((term, parse_float(value)))
    rows.sort(key=lambda item: (-item[1], item[0]))
    return rows


def iter_score_files(directory: Path, only: str | None) -> list[Path]:
    files = sorted(p for p in directory.iterdir() if p.is_file() and p.suffix == ".txt")
    if only:
        files = [p for p in files if p.name == only]
        if not files:
            raise SystemExit(f"{only} not found in {directory}")
    return files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dir", type=Path, default=Path("output/tfidf"))
    parser.add_argument("--file", dest="only", default=None, help="single filename")
    parser.add_argument("--k", type=int, default=12, help="rows to print per file")
    parser.add_argument(
        "--zeros",
        action="store_true",
        help="also print how many terms scored exactly 0",
    )
    args = parser.parse_args(argv)

    for path in iter_score_files(args.dir, args.only):
        rows = load_scores(path)
        print(f"## {path.name}")
        for term, score in rows[: args.k]:
            print(f"  {term:20} {score:.8g}")
        if args.zeros:
            n_zero = sum(1 for _, score in rows if score == 0.0)
            print(f"  [zeros={n_zero} / vocab={len(rows)}]")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
