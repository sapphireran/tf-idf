#!/usr/bin/env python3
"""Rank alphabetical TF or TF-IDF dumps by score.

Against the committed Gutenberg run:

    python3 examples/rank_terms.py --input-dir output/tfidf --top 15
    python3 examples/rank_terms.py --input-dir output/tfidf --only carroll-alice.txt
    python3 examples/rank_terms.py --input-dir output/tf --top 10

Against a folder this script just wrote (term<TAB>score lines):

    python3 examples/rank_terms.py --input-dir /tmp/toy-tfidf
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from tfidf_lib import format_table, parse_tsv_scores, rank_score_map  # noqa: E402


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("output/tfidf"),
        help="Directory of term<TAB>score files (default: output/tfidf)",
    )
    parser.add_argument(
        "--only",
        action="append",
        default=[],
        help="Restrict to these filenames (repeatable)",
    )
    parser.add_argument("--top", type=int, default=15, help="How many rows per file")
    parser.add_argument(
        "--min-score",
        type=float,
        default=None,
        help="Drop terms at or below this score (useful for skipping exact zeros)",
    )
    return parser.parse_args(argv)


def iter_score_files(directory: Path, only: list[str]) -> list[Path]:
    wanted = set(only)
    files = sorted(
        path
        for path in directory.iterdir()
        if path.is_file() and path.suffix == ".txt" and not path.name.startswith(".")
    )
    if wanted:
        files = [path for path in files if path.name in wanted]
        missing = wanted - {path.name for path in files}
        if missing:
            raise SystemExit(f"not found in {directory}: {', '.join(sorted(missing))}")
    if not files:
        raise SystemExit(f"no .txt score files in {directory}")
    return files


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.input_dir.is_dir():
        raise SystemExit(f"not a directory: {args.input_dir}")

    for path in iter_score_files(args.input_dir, args.only):
        scores = parse_tsv_scores(path)
        ranked = rank_score_map(scores)
        if args.min_score is not None:
            ranked = [(term, score) for term, score in ranked if score > args.min_score]
        ranked = ranked[: args.top]
        rows = [(i + 1, term, f"{score:.12g}") for i, (term, score) in enumerate(ranked)]
        print(f"# {path.name}  ({len(scores)} terms)")
        print(format_table(rows, ("rank", "term", "score")))
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
