#!/usr/bin/env python3
"""Show Folio tokens that glue the three Shakespeare files together."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from shelf import Shelf  # noqa: E402

PLAYS = (
    "shakespeare-caesar.txt",
    "shakespeare-hamlet.txt",
    "shakespeare-macbeth.txt",
)
FOLIO_PROBE = ("haue", "vpon", "selfe", "vs", "giue", "heere", "loue")


def shared_spine(shelf: Shelf, limit: int) -> list[tuple[str, list[float]]]:
    shared = set(shelf.tfidf[PLAYS[0]])
    for play in PLAYS[1:]:
        shared &= set(shelf.tfidf[play])
    ranked: list[tuple[str, list[float]]] = []
    for term in shared:
        scores = [shelf.tfidf[play].get(term, 0.0) for play in PLAYS]
        if min(scores) <= 0.0:
            continue
        ranked.append((term, scores))
    ranked.sort(key=lambda item: (-min(item[1]), -sum(item[1]), item[0]))
    return ranked[:limit]


def print_spine(shelf: Shelf, limit: int) -> None:
    print(f"{'term':<12} {'caesar':>8} {'hamlet':>8} {'macbeth':>8} {'min':>8}")
    for term, scores in shared_spine(shelf, limit):
        print(
            f"{term:<12} {scores[0]:8.5f} {scores[1]:8.5f} "
            f"{scores[2]:8.5f} {min(scores):8.5f}"
        )


def print_presence(shelf: Shelf) -> None:
    print()
    print("Files with a non-zero weight for selected Folio tokens:")
    for term in FOLIO_PROBE:
        hosts = shelf.documents_containing(term)
        labels = ", ".join(shelf.short_name(name) for name in hosts) or "(none)"
        print(f"  {term:<8} {len(hosts):2d}  {labels}")


def check(shelf: Shelf) -> int:
    for term in ("haue", "vpon", "selfe"):
        hosts = set(shelf.documents_containing(term))
        if hosts != set(PLAYS):
            print(f"FAIL: {term} hosts={sorted(hosts)}", file=sys.stderr)
            return 1

    spine = shared_spine(shelf, 1)
    if not spine or spine[0][0] != "haue":
        print(f"FAIL: shared spine head is {spine}", file=sys.stderr)
        return 1

    ranked = shelf.rank_query(["haue", "vpon", "selfe"])
    top_three = [name for _, name in ranked[:3]]
    if set(top_three) != set(PLAYS):
        print(f"FAIL: Folio query top-3 {top_three}", file=sys.stderr)
        return 1
    if ranked[3][0] > 1e-9:
        print(
            f"FAIL: fourth Folio-query hit should be ~0, got {ranked[3]}",
            file=sys.stderr,
        )
        return 1

    print(
        "folio_spellings checks passed: "
        f"haue min={min(spine[0][1]):.5f}, "
        f"query-1={shelf.short_name(ranked[0][1])} {ranked[0][0]:.4f}"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--top", type=int, default=15)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--root", type=Path, default=None)
    args = parser.parse_args(argv)
    shelf = Shelf.load(args.root)
    if args.check:
        return check(shelf)
    print_spine(shelf, args.top)
    print_presence(shelf)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
