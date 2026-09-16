#!/usr/bin/env python3
"""Print the heaviest TF-IDF terms for one book or the whole shelf."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from shelf import Shelf  # noqa: E402

LOCKED_TOP = {
    "carroll-alice.txt": "alice",
    "melville-moby_dick.txt": "whale",
    "burgess-busterbrown.txt": "buster",
    "austen-emma.txt": "emma",
    "austen-sense.txt": "elinor",
    "bible-kjv.txt": "unto",
    "milton-paradise.txt": "thee",
    "whitman-leaves.txt": "o",
    "shakespeare-macbeth.txt": "macb",
    "shakespeare-hamlet.txt": "ham",
    "shakespeare-caesar.txt": "bru",
    "chesterton-thursday.txt": "syme",
    "chesterton-ball.txt": "turnbull",
    "chesterton-brown.txt": "flambeau",
}


def resolve_document(shelf: Shelf, needle: str) -> str:
    if needle in shelf.tfidf:
        return needle
    if not needle.endswith(".txt"):
        guess = needle + ".txt"
        if guess in shelf.tfidf:
            return guess
    matches = [
        name
        for name in shelf.documents
        if needle in name or needle in shelf.short_name(name)
    ]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise SystemExit(f"No document matches {needle!r}")
    raise SystemExit("Ambiguous document: " + ", ".join(matches))


def print_atlas(shelf: Shelf, filename: str, top: int) -> None:
    print(f"== {filename} ==")
    for term, score in shelf.top_terms(filename, top):
        print(f"  {score:8.5f}  {term}")


def check(shelf: Shelf) -> int:
    for filename, expected in LOCKED_TOP.items():
        term, score = shelf.heaviest_term(filename)
        if term != expected:
            print(
                f"FAIL: {filename} top term {term}, expected {expected}",
                file=sys.stderr,
            )
            return 1
        if score <= 0:
            print(f"FAIL: {filename} non-positive top score", file=sys.stderr)
            return 1
    print(f"term_atlas checks passed: {len(LOCKED_TOP)} locked top terms")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "document",
        nargs="?",
        help="Filename or unique substring (default: every book)",
    )
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--root", type=Path, default=None)
    args = parser.parse_args(argv)
    shelf = Shelf.load(args.root)
    if args.check:
        return check(shelf)
    names = (
        [resolve_document(shelf, args.document)]
        if args.document
        else shelf.documents
    )
    for name in names:
        print_atlas(shelf, name, args.top)
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
