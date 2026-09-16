#!/usr/bin/env python3
"""Show how the personal toy tokenizer turns a line into terms.

Useful when a word you expected (won't, Alice's, Moby-Dick) disappears
or fuses into a neighbor. The rules copy tf-idf-values.pl:

1. lowercase
2. squeeze horizontal/vertical whitespace to a single space
3. drop every character that is not a letter, digit, or space
4. split on spaces and throw away empty tokens
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Import the shared tokenizer from the tiny example.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from tiny_tfidf import tokenize  # noqa: E402


SAMPLES = [
    "Alice was beginning to get very tired.",
    "Alice's Adventures in Wonderland",
    "won't, can't, 'tis",
    "Moby-Dick; or, The Whale.",
    "Call me Ishmael.",
    "HAMLET. To be, or not to be:",
    "thetable (words fused when punctuation is the only separator)",
]


def show(label: str, text: str) -> None:
    tokens = tokenize(text)
    print(f"in : {text}")
    print(f"out: {tokens}")
    print(f"     {len(tokens)} token(s) [{label}]")
    print()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "text",
        nargs="*",
        help="optional lines to tokenize; defaults to a built-in sampler",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.text:
        show("argv", " ".join(args.text))
        return 0
    for index, sample in enumerate(SAMPLES, start=1):
        show(f"sample {index}", sample)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
