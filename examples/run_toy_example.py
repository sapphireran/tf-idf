#!/usr/bin/env python3
"""Run tf-idf on examples/toy-corpus and print every intermediate table.

Numbers are meant to be checked against examples/worked-example.md.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow `python3 examples/run_toy_example.py` from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from tfidf_mini import analyze_directory, format_float, ranked  # noqa: E402

TOY = Path(__file__).resolve().parent / "toy-corpus"


def print_section(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--corpus",
        type=Path,
        default=TOY,
        help="Directory of tiny documents (default: examples/toy-corpus)",
    )
    parser.add_argument(
        "--clean-denom",
        action="store_true",
        help="Count only non-empty tokens in tf (default mirrors Perl, including empties)",
    )
    args = parser.parse_args()

    result = analyze_directory(args.corpus, faithful=not args.clean_denom)
    print(f"corpus: {args.corpus}")
    print(f"N documents: {result['n_docs']}")
    print(f"denominator: {'perl-faithful (includes empty fields)' if result['faithful'] else 'non-empty tokens only'}")

    print_section("tokens (non-empty)")
    for name, fields in result["fields"].items():
        tokens = [t for t in fields if t]
        print(f"{name}: n={len(tokens)}  {' '.join(tokens)}")

    print_section("term frequency")
    for name, tf in result["tf"].items():
        parts = [f"{term}={format_float(weight)}" for term, weight in sorted(tf.items())]
        print(f"{name}: " + ", ".join(parts))

    print_section("document frequency and idf  (idf = ln(N / df))")
    print(f"{'term':<14} {'df':>4}  {'idf':>12}  documents")
    for term in sorted(result["idf"]):
        names = ", ".join(sorted(result["df"][term]))
        df = len(result["df"][term])
        print(f"{term:<14} {df:>4}  {format_float(result['idf'][term]):>12}  {names}")

    print_section("tf-idf by document (highest first)")
    for name, table in result["tfidf"].items():
        print(f"\n{name}")
        for term, weight in ranked(table):
            flag = "  <-- top" if weight == ranked(table, 1)[0][1] and weight > 0 else ""
            print(f"  {term:<14} {format_float(weight)}{flag}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
