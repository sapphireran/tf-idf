#!/usr/bin/env python3
"""Look up one token, or summarize the frozen 2012 snapshot."""

from __future__ import annotations

import argparse
from pathlib import Path

import _paths
from tfidfkit.tables import load_committed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=_paths.REPO_ROOT / "output",
        help="Snapshot directory (default: repository output/)",
    )
    parser.add_argument("--token", help="Inspect one token across the snapshot")
    parser.add_argument("--summary", action="store_true", help="Print corpus-level counts")
    args = parser.parse_args()

    tables = load_committed(args.output_root)
    if args.summary or not args.token:
        zero = sorted(token for token, value in tables.idf.items() if value == 0.0)
        hapax = sum(1 for df, _names in tables.df.values() if df == 1)
        print(f"documents\t{len(tables.tfidf)}")
        print(f"vocabulary\t{len(tables.idf)}")
        print(f"df=1\t{hapax}")
        print(f"idf=0\t{len(zero)}")
        print(f"dirty_idf\t{len(tables.dirty_idf)}")
        if tables.dirty_idf:
            print(f"dirty_idf_tokens\t{', '.join(tables.dirty_idf)}")
        if not args.token:
            return 0

    token = args.token
    if token not in tables.idf and token not in tables.df:
        raise SystemExit(f"unknown token: {token}")

    df, names = tables.df.get(token, (0, ()))
    print(f"token\t{token}")
    print(f"df\t{df}")
    print(f"idf\t{tables.idf.get(token, float('nan'))}")
    print(f"postings\t{', '.join(names)}")
    print("document\ttf\ttfidf")
    for name in sorted(tables.tfidf):
        if token not in tables.tf.get(name, {}) and token not in tables.tfidf.get(name, {}):
            continue
        tf = tables.tf.get(name, {}).get(token, 0.0)
        tfidf = tables.tfidf.get(name, {}).get(token, 0.0)
        print(f"{name}\t{tf:.8g}\t{tfidf:.8g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
