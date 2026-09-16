#!/usr/bin/env python3
"""Inspect the committed Gutenberg TF-IDF tables without rerunning Perl.

The precomputed files in ``output/tfidf/`` are the original toy result.
This script only reads them. It is the safe way to explore distinctive
terms for Alice, Moby-Dick, Hamlet, and the rest of the personal sample.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from tfidf_lab import read_term_weights, top_terms_from_weights


DEFAULT_TITLES = {
    "austen-emma.txt": "Emma — Jane Austen",
    "austen-persuasion.txt": "Persuasion — Jane Austen",
    "austen-sense.txt": "Sense and Sensibility — Jane Austen",
    "bible-kjv.txt": "King James Bible",
    "blake-poems.txt": "Poems — William Blake",
    "bryant-stories.txt": "Stories — Bryant",
    "burgess-busterbrown.txt": "Buster Brown — Burgess",
    "carroll-alice.txt": "Alice's Adventures in Wonderland — Carroll",
    "chesterton-ball.txt": "The Ball and the Cross — Chesterton",
    "chesterton-brown.txt": "Father Brown — Chesterton",
    "chesterton-thursday.txt": "The Man Who Was Thursday — Chesterton",
    "edgeworth-parents.txt": "The Parent's Assistant — Edgeworth",
    "melville-moby_dick.txt": "Moby-Dick — Melville",
    "milton-paradise.txt": "Paradise Lost — Milton",
    "shakespeare-caesar.txt": "Julius Caesar — Shakespeare",
    "shakespeare-hamlet.txt": "Hamlet — Shakespeare",
    "shakespeare-macbeth.txt": "Macbeth — Shakespeare",
    "whitman-leaves.txt": "Leaves of Grass — Whitman",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dir",
        type=Path,
        default=ROOT / "output" / "tfidf",
        help="directory of committed TF-IDF TSV files",
    )
    parser.add_argument("-n", "--top", type=int, default=10)
    parser.add_argument(
        "--only",
        nargs="*",
        default=None,
        help="optional filenames to include, e.g. carroll-alice.txt",
    )
    args = parser.parse_args()

    if not args.dir.is_dir():
        print(f"missing {args.dir}", file=sys.stderr)
        return 1

    names = sorted(
        path.name
        for path in args.dir.iterdir()
        if path.suffix == ".txt" and not path.name.startswith(".")
    )
    if args.only:
        wanted = set(args.only)
        names = [name for name in names if name in wanted]

    for name in names:
        title = DEFAULT_TITLES.get(name, name)
        weights = read_term_weights(args.dir / name)
        print(f"== {title}")
        print(f"   file={name}  terms={len(weights)}")
        for term, score in top_terms_from_weights(weights, args.top):
            print(f"   {term:20s} {score:.6f}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
