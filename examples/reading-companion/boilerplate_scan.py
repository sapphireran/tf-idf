#!/usr/bin/env python3
"""Count Gutenberg-trailer tokens in the raw files vs snapshot weights."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from shelf import Shelf  # noqa: E402

TRAILER_TERMS = ("gutenberg", "ebook", "ebooks")
TOKEN_RE = re.compile(r"[a-z0-9]+")


def raw_counts(path: Path) -> dict[str, int]:
    text = path.read_text(encoding="utf-8", errors="replace").lower()
    # Match the 2012 "letters and digits only" spirit well enough to
    # count wrapper words. Apostrophes are already gone after lower+filter.
    tokens = TOKEN_RE.findall(text)
    return {term: tokens.count(term) for term in TRAILER_TERMS}


def print_scan(shelf: Shelf) -> None:
    print(
        f"{'book':<24} {'gut':>5} {'ebook':>6} {'ebooks':>6}  "
        f"{'w-gut':>8} {'w-ebook':>8} {'w-ebooks':>8}"
    )
    rows = []
    for name in shelf.documents:
        counts = raw_counts(shelf.root / "gutenberg" / name)
        vec = shelf.tfidf[name]
        rows.append((sum(counts.values()), name, counts, vec))
    for _, name, counts, vec in sorted(rows, reverse=True):
        print(
            f"{shelf.short_name(name):<24} "
            f"{counts['gutenberg']:5d} {counts['ebook']:6d} {counts['ebooks']:6d}  "
            f"{vec.get('gutenberg', 0.0):8.5f} "
            f"{vec.get('ebook', 0.0):8.5f} "
            f"{vec.get('ebooks', 0.0):8.5f}"
        )


def check(shelf: Shelf) -> int:
    totals: list[tuple[int, str]] = []
    for name in shelf.documents:
        counts = raw_counts(shelf.root / "gutenberg" / name)
        totals.append((sum(counts.values()), name))
    totals.sort(reverse=True)
    winner_total, winner = totals[0]
    if winner != "chesterton-ball.txt":
        print(f"FAIL: trailer-count winner is {winner}", file=sys.stderr)
        return 1
    if winner_total < 40:
        print(f"FAIL: Ball trailer count only {winner_total}", file=sys.stderr)
        return 1

    ball = shelf.tfidf["chesterton-ball.txt"]
    if ball.get("ebook", 0.0) < 0.0009:
        print(f"FAIL: ebook weight in Ball is {ball.get('ebook')}", file=sys.stderr)
        return 1
    if ball.get("gutenberg", 0.0) < 0.0007:
        print(
            f"FAIL: gutenberg weight in Ball is {ball.get('gutenberg')}",
            file=sys.stderr,
        )
        return 1

    # Trailer words should be rare on the rest of the shelf.
    others = [
        name
        for name in shelf.documents
        if name != "chesterton-ball.txt" and shelf.tfidf[name].get("ebook", 0.0) > 0
    ]
    if others:
        print(f"FAIL: ebook leaked into {others}", file=sys.stderr)
        return 1

    print(
        "boilerplate_scan checks passed: "
        f"Ball raw-trailer-tokens={winner_total}, "
        f"ebook-weight={ball['ebook']:.5f}"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--root", type=Path, default=None)
    args = parser.parse_args(argv)
    shelf = Shelf.load(args.root)
    if args.check:
        return check(shelf)
    print_scan(shelf)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
