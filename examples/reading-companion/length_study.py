#!/usr/bin/env python3
"""Tabulate raw length, vocab, top term, and vector L2 for each book."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from shelf import Shelf  # noqa: E402


def rows(shelf: Shelf) -> list[tuple[int, int, str, float, float, str]]:
    table = []
    for name in shelf.documents:
        term, weight = shelf.heaviest_term(name)
        table.append(
            (
                shelf.raw_word_count(name),
                len(shelf.tfidf[name]),
                term,
                weight,
                shelf.norms[name],
                name,
            )
        )
    return table


def print_table(shelf: Shelf) -> None:
    print(
        f"{'book':<24} {'words':>8} {'vocab':>6} {'top':<12} "
        f"{'tfidf':>8} {'L2':>7}"
    )
    for words, vocab, term, weight, norm, name in sorted(
        rows(shelf), key=lambda row: -row[3]
    ):
        print(
            f"{shelf.short_name(name):<24} {words:8d} {vocab:6d} "
            f"{term:<12} {weight:8.5f} {norm:7.5f}"
        )


def check(shelf: Shelf) -> int:
    table = rows(shelf)
    heaviest = max(table, key=lambda row: row[3])
    lightest = min(table, key=lambda row: row[3])
    spiked = max(table, key=lambda row: row[4])

    if heaviest[2] != "buster" or heaviest[5] != "burgess-busterbrown.txt":
        print(
            f"FAIL: heaviest term is {heaviest[2]} in {heaviest[5]}",
            file=sys.stderr,
        )
        return 1
    if heaviest[3] < 0.04:
        print(f"FAIL: buster weight drifted to {heaviest[3]}", file=sys.stderr)
        return 1
    if lightest[5] != "whitman-leaves.txt" or lightest[2] != "o":
        print(
            f"FAIL: lightest top-term is {lightest[2]} in {lightest[5]}",
            file=sys.stderr,
        )
        return 1
    if spiked[5] != "burgess-busterbrown.txt":
        print(f"FAIL: largest L2 is {spiked[5]}", file=sys.stderr)
        return 1

    moby = next(row for row in table if row[5] == "melville-moby_dick.txt")
    if moby[2] != "whale":
        print(f"FAIL: Moby-Dick top term is {moby[2]}", file=sys.stderr)
        return 1

    print(
        "length_study checks passed: "
        f"buster={heaviest[3]:.5f}, whitman-o={lightest[3]:.5f}, "
        f"burgess-L2={spiked[4]:.5f}"
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
    print_table(shelf)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
