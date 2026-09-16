#!/usr/bin/env python3
"""Print pairwise cosines, nearest neighbors, and author-group means."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from shelf import Shelf  # noqa: E402

SHAKESPEARE = (
    "shakespeare-caesar.txt",
    "shakespeare-hamlet.txt",
    "shakespeare-macbeth.txt",
)
AUSTEN = (
    "austen-emma.txt",
    "austen-persuasion.txt",
    "austen-sense.txt",
)
CHESTERTON = (
    "chesterton-ball.txt",
    "chesterton-brown.txt",
    "chesterton-thursday.txt",
)

GROUPS = {
    "shakespeare": SHAKESPEARE,
    "austen": AUSTEN,
    "chesterton": CHESTERTON,
}


def print_pairs(shelf: Shelf, limit: int | None) -> None:
    pairs = shelf.pairwise()
    shown = pairs if limit is None else pairs[:limit]
    print(f"{'cosine':>8}  left  ~  right")
    for score, left, right in shown:
        print(
            f"{score:8.4f}  {shelf.short_name(left)}  ~  {shelf.short_name(right)}"
        )


def print_neighbors(shelf: Shelf) -> None:
    print(f"{'book':<24}  {'1st':<22} {'cos':>6}  {'2nd':<22} {'cos':>6}")
    for name in shelf.documents:
        n1, n2 = shelf.neighbors(name, k=2)
        print(
            f"{shelf.short_name(name):<24}  "
            f"{shelf.short_name(n1[1]):<22} {n1[0]:6.4f}  "
            f"{shelf.short_name(n2[1]):<22} {n2[0]:6.4f}"
        )


def print_groups(shelf: Shelf, only: str | None) -> None:
    names = [only] if only else list(GROUPS)
    for key in names:
        files = GROUPS[key]
        mean = shelf.group_mean(files)
        print(f"{key:12} intra-mean {mean:.4f}")
        for i, left in enumerate(files):
            for right in files[i + 1 :]:
                score = shelf.pair_cosine(left, right)
                print(
                    f"  {score:.4f}  {shelf.short_name(left)}  ~  "
                    f"{shelf.short_name(right)}"
                )


def check(shelf: Shelf) -> int:
    pairs = shelf.pairwise()
    top_score, top_left, top_right = pairs[0]
    names = {top_left, top_right}
    if names != {"shakespeare-hamlet.txt", "shakespeare-macbeth.txt"}:
        print(
            f"FAIL: expected Hamlet~Macbeth as closest pair, got "
            f"{top_left} ~ {top_right}",
            file=sys.stderr,
        )
        return 1
    if top_score < 0.308:
        print(f"FAIL: Hamlet~Macbeth cosine drifted to {top_score}", file=sys.stderr)
        return 1

    low_score, low_left, low_right = pairs[-1]
    low_names = {low_left, low_right}
    if low_names != {"burgess-busterbrown.txt", "shakespeare-caesar.txt"}:
        print(
            f"FAIL: expected Buster~Caesar as lowest pair, got "
            f"{low_left} ~ {low_right}",
            file=sys.stderr,
        )
        return 1
    if low_score > 0.0003:
        print(f"FAIL: lowest pair drifted up to {low_score}", file=sys.stderr)
        return 1

    sh_mean = shelf.group_mean(SHAKESPEARE)
    au_mean = shelf.group_mean(AUSTEN)
    ch_mean = shelf.group_mean(CHESTERTON)
    if not (0.25 < sh_mean < 0.28):
        print(f"FAIL: Shakespeare mean {sh_mean}", file=sys.stderr)
        return 1
    if not (0.07 < au_mean < 0.08):
        print(f"FAIL: Austen mean {au_mean}", file=sys.stderr)
        return 1
    if not (0.03 < ch_mean < 0.05):
        print(f"FAIL: Chesterton mean {ch_mean}", file=sys.stderr)
        return 1

    first = shelf.neighbors("austen-persuasion.txt", k=1)[0]
    if first[1] != "edgeworth-parents.txt":
        print(
            f"FAIL: Persuasion neighbor is {first[1]}, not Edgeworth",
            file=sys.stderr,
        )
        return 1

    print(
        "cosine_map checks passed: "
        f"Hamlet~Macbeth={top_score:.4f}, "
        f"Buster~Caesar={low_score:.6f}, "
        f"means sh={sh_mean:.4f} au={au_mean:.4f} ch={ch_mean:.4f}"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="How many strongest pairs to print (0 = all)",
    )
    parser.add_argument("--neighbors", action="store_true")
    parser.add_argument("--group", choices=sorted(GROUPS), default=None)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--root", type=Path, default=None)
    args = parser.parse_args(argv)

    shelf = Shelf.load(args.root)
    if args.check:
        return check(shelf)
    if args.group:
        print_groups(shelf, args.group)
        return 0
    if args.neighbors:
        print_neighbors(shelf)
        return 0
    limit = None if args.top == 0 else args.top
    print_pairs(shelf, limit)
    print()
    print_groups(shelf, None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
