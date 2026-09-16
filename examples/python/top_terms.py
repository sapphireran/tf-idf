#!/usr/bin/env python3
"""Print the highest-scoring terms from a TF or TF-IDF TSV file.

PATH may be a single two-column TSV or a directory of them (the
layout of output/tfidf/).

Example:

    python3 examples/python/top_terms.py output/tfidf --top 10
    python3 examples/python/top_terms.py output/tfidf/carroll-alice.txt
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from tfidf_lib import read_score_tsv, top_terms


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="TSV file or directory of TSV files")
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="How many terms to print per file (default: 10)",
    )
    return parser.parse_args(argv)


def iter_targets(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if path.is_dir():
        files = [
            child
            for child in path.iterdir()
            if child.is_file() and not child.name.startswith(".")
        ]
        return sorted(files, key=lambda child: child.name)
    raise FileNotFoundError(path)


def render_file(path: Path, limit: int) -> str:
    scores = read_score_tsv(path)
    ranked = top_terms(scores, limit)
    lines = [f"== {path.name}"]
    width = max((len(term) for term, _ in ranked), default=0)
    for term, value in ranked:
        lines.append(f"  {term:<{width}}  {value:.8f}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.top < 0:
        print("--top must be >= 0", file=sys.stderr)
        return 2
    try:
        targets = iter_targets(args.path)
    except FileNotFoundError:
        print(f"path not found: {args.path}", file=sys.stderr)
        return 2
    if not targets:
        print(f"no TSV files in {args.path}", file=sys.stderr)
        return 2
    blocks = [render_file(path, args.top) for path in targets]
    print("\n\n".join(blocks))
    return 0


if __name__ == "__main__":
    sys.exit(main())
