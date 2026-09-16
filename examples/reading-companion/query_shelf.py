#!/usr/bin/env python3
"""Rank the eighteen books against a bag-of-tokens query."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from shelf import Shelf  # noqa: E402

# Cookbook recipes locked in docs/reading-companion/09-query-cookbook.md
RECIPES: list[tuple[str, str, float, float]] = [
    # query, expected winner file, min winner cosine, max runner-up cosine
    ("elinor marianne dashwood", "austen-sense.txt", 0.79, 0.06),
    ("alice hatter gryphon dormouse", "carroll-alice.txt", 0.67, 0.01),
    ("syme anarchist professor", "chesterton-thursday.txt", 0.64, 0.02),
    ("buster otter mink", "burgess-busterbrown.txt", 0.60, 0.02),
    ("unto israel moses david", "bible-kjv.txt", 0.60, 0.12),
    (
        "emma knightley hartfield woodhouse",
        "austen-emma.txt",
        0.56,
        0.01,
    ),
    (
        "brutus cassius antony caesar",
        "shakespeare-caesar.txt",
        0.50,
        0.01,
    ),
    ("flambeau priest brown", "chesterton-brown.txt", 0.47, 0.02),
    ("white whale ahab pequod", "melville-moby_dick.txt", 0.47, 0.04),
    ("satan eve adam heaven", "milton-paradise.txt", 0.29, 0.02),
    ("manhattan pioneers chant", "whitman-leaves.txt", 0.18, 0.02),
    ("macbeth witches thane cawdor", "shakespeare-macbeth.txt", 0.24, 0.01),
]


def print_ranking(shelf: Shelf, tokens: list[str], k: int) -> None:
    print("query:", " ".join(tokens))
    for score, name in shelf.rank_query(tokens)[:k]:
        print(f"  {score:7.4f}  {shelf.short_name(name)}")


def check(shelf: Shelf) -> int:
    for query, winner, min_win, max_second in RECIPES:
        ranked = shelf.rank_query(query.split())
        top_score, top_name = ranked[0]
        second_score, second_name = ranked[1]
        if top_name != winner:
            print(
                f"FAIL: {query!r} winner {top_name}, expected {winner}",
                file=sys.stderr,
            )
            return 1
        if top_score < min_win:
            print(
                f"FAIL: {query!r} winner cosine {top_score} < {min_win}",
                file=sys.stderr,
            )
            return 1
        if second_score > max_second:
            print(
                f"FAIL: {query!r} runner-up {second_name} "
                f"{second_score} > {max_second}",
                file=sys.stderr,
            )
            return 1

    zeros = shelf.rank_query(["the", "and", "of"])
    if any(score > 1e-12 for score, _ in zeros):
        print("FAIL: stopword query should be all zeros", file=sys.stderr)
        return 1

    folio = shelf.rank_query(["haue", "vpon", "selfe"])
    folio_top = {name for _, name in folio[:3]}
    expected = {
        "shakespeare-caesar.txt",
        "shakespeare-hamlet.txt",
        "shakespeare-macbeth.txt",
    }
    if folio_top != expected:
        print(f"FAIL: Folio query top-3 {folio_top}", file=sys.stderr)
        return 1
    if folio[3][0] > 1e-9:
        print(f"FAIL: Folio query leaked to {folio[3]}", file=sys.stderr)
        return 1

    print(f"query_shelf checks passed: {len(RECIPES)} recipes + stopwords + Folio")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tokens", nargs="*", help="Query tokens (already words)")
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--root", type=Path, default=None)
    args = parser.parse_args(argv)
    shelf = Shelf.load(args.root)
    if args.check:
        return check(shelf)
    if not args.tokens:
        parser.error("pass query tokens, or --check")
    print_ranking(shelf, args.tokens, args.k)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
