#!/usr/bin/env python3
"""Run the two-pass tf * idf pipeline on a directory of text files."""

from __future__ import annotations

import argparse
from pathlib import Path

import _paths  # noqa: F401
from tfidfkit.tables import write_pipeline_tree
from tfidfkit.weights import run_pipeline


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Directory of .txt documents",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Directory to write tf/, df.txt, idf.txt, tfidf/",
    )
    parser.add_argument(
        "--compat-empty-tokens",
        action="store_true",
        help="Count leading empty split fields in the TF denominator, like the Perl script",
    )
    args = parser.parse_args()

    result = run_pipeline(
        args.input, count_empty_tokens=args.compat_empty_tokens
    )
    write_pipeline_tree(args.output, result.tf, result.df, result.idf, result.tfidf)

    unique = sum(1 for docs in result.df.values() if len(docs) == 1)
    zero_idf = sum(1 for value in result.idf.values() if value == 0.0)
    print(f"documents\t{result.n_documents}")
    print(f"vocabulary\t{len(result.idf)}")
    print(f"df=1\t{unique}")
    print(f"idf=0\t{zero_idf}")
    print(f"wrote\t{args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
