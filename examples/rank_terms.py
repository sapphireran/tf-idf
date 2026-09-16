#!/usr/bin/env python3
"""Rank a TF-IDF (or TF / IDF) TSV the way the Perl scripts write them.

The checked-in ``output/tfidf/*.txt`` files are ``term<TAB>score`` rows.
GNU ``sort -n`` stops at the first non-numeric character, so a value like
``9.89e-05`` is treated as ``9.89`` and jumps to the top of a descending
sort. Use this helper, or ``sort -g``, when you want the real ranking.

Examples:

    python3 examples/rank_terms.py output/tfidf/carroll-alice.txt
    python3 examples/rank_terms.py output/tfidf/melville-moby_dick.txt -n 15
    python3 examples/rank_terms.py output/tfidf/carroll-alice.txt \\
        --versus output/tfidf/melville-moby_dick.txt
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def load_scores(path: Path) -> list[tuple[str, float]]:
    rows: list[tuple[str, float]] = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if not raw or raw.startswith("word \t"):
            continue
        parts = raw.split("\t")
        if len(parts) < 2:
            continue
        term, score_text = parts[0], parts[1]
        try:
            score = float(score_text)
        except ValueError:
            print(f"{path}:{line_no}: skip unreadable score {score_text!r}", file=sys.stderr)
            continue
        rows.append((term, score))
    rows.sort(key=lambda item: (-item[1], item[0]))
    return rows


def format_table(rows: list[tuple[str, float]], limit: int) -> str:
    width = max((len(term) for term, _ in rows[:limit]), default=4)
    width = max(width, 4)
    lines = [f"{'term':<{width}}  score"]
    lines.append(f"{'-' * width}  ----------")
    for term, score in rows[:limit]:
        lines.append(f"{term:<{width}}  {score:.8g}")
    return "\n".join(lines)


def contrast(
    left: list[tuple[str, float]],
    right: list[tuple[str, float]],
    limit: int,
) -> str:
    """Terms that rank high on the left and are missing or weak on the right."""
    right_score = {term: score for term, score in right}
    right_rank = {term: idx for idx, (term, _) in enumerate(right, 1)}
    leftovers: list[tuple[str, float, float, str]] = []
    for term, score in left:
        if term not in right_score:
            leftovers.append((term, score, 0.0, "absent"))
        elif right_score[term] < score * 0.25:
            leftovers.append((term, score, right_score[term], f"rank {right_rank[term]}"))
        if len(leftovers) >= limit:
            break

    width = max((len(row[0]) for row in leftovers), default=4)
    width = max(width, 4)
    lines = [f"{'term':<{width}}  left score   right       note"]
    lines.append(f"{'-' * width}  ----------  ----------  ----")
    for term, left_score, right_val, note in leftovers:
        lines.append(f"{term:<{width}}  {left_score:.8g}  {right_val:.8g}  {note}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tsv", type=Path, help="term<TAB>score file from output/tf, output/idf, or output/tfidf")
    parser.add_argument("-n", "--top", type=int, default=20, help="rows to print (default 20)")
    parser.add_argument(
        "--versus",
        type=Path,
        help="optional second TSV; print terms that are strong in the first file and weak in the second",
    )
    args = parser.parse_args(argv)

    if not args.tsv.is_file():
        print(f"not a file: {args.tsv}", file=sys.stderr)
        return 2

    left = load_scores(args.tsv)
    print(f"{args.tsv}  ({len(left)} terms)")
    print(format_table(left, args.top))

    if args.versus:
        if not args.versus.is_file():
            print(f"not a file: {args.versus}", file=sys.stderr)
            return 2
        right = load_scores(args.versus)
        print()
        print(f"strong in {args.tsv.name}, weak or missing in {args.versus.name}")
        print(contrast(left, right, args.top))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
