#!/usr/bin/env python3
"""Compute TF-IDF for every non-hidden file in a directory.

Writes the same artifact layout as the original Perl pipeline:

    <output>/tf/<file>
    <output>/idf.txt
    <output>/df.txt
    <output>/tfidf/<file>

Example:

    python3 examples/python/compute_tfidf.py \\
        --input-dir examples/tiny-corpus \\
        --output-dir /tmp/tiny-tfidf
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from tfidf_lib import score_collection, write_collection


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-dir",
        required=True,
        type=Path,
        help="Directory of documents (non-hidden files only)",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Directory to create tf/, tfidf/, df.txt, idf.txt",
    )
    parser.add_argument(
        "--count-empty-tokens",
        action="store_true",
        help="Count empty split fields in the TF denominator (Perl quirk)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.input_dir.is_dir():
        print(f"input directory not found: {args.input_dir}", file=sys.stderr)
        return 2
    scores = score_collection(
        args.input_dir, count_empty=args.count_empty_tokens
    )
    write_collection(scores, args.output_dir)
    print(f"N={scores.n_docs} documents")
    print(f"V={len(scores.idf)} terms")
    print(f"wrote {args.output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
