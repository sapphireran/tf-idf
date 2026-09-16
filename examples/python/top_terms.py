#!/usr/bin/env python3
"""Print the highest-scoring terms from a TF-IDF TSV file or directory."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from tfidf_lab import read_term_weights, top_terms_from_weights


def collect_paths(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    return sorted(
        path
        for path in target.iterdir()
        if path.is_file() and path.suffix == ".txt" and not path.name.startswith(".")
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="TF-IDF TSV file or directory")
    parser.add_argument("-n", "--top", type=int, default=12)
    args = parser.parse_args()

    paths = collect_paths(args.path)
    if not paths:
        print(f"no TSV files in {args.path}", file=sys.stderr)
        return 1

    for path in paths:
        weights = read_term_weights(path)
        print(f"== {path.name} ({len(weights)} terms) ==")
        for term, score in top_terms_from_weights(weights, args.top):
            print(f"  {term:20s} {score:.6f}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
