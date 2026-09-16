#!/usr/bin/env python3
"""Trace one token through the committed Gutenberg tables.

    python3 examples/follow_word.py alice
    python3 examples/follow_word.py whale
    python3 examples/follow_word.py the
    python3 examples/follow_word.py unto --top-docs 5
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from tfidf_lib import format_table, parse_df_table, parse_tsv_scores  # noqa: E402


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("term", help="Token after the Perl tokenizer (already lowercase, no punctuation)")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "output")
    parser.add_argument("--n-docs", type=int, default=18, help="N used by the committed IDF table")
    parser.add_argument("--top-docs", type=int, default=None, help="Show only the documents with the highest TF-IDF")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    term = args.term.lower()
    output = args.output_dir

    idf_path = output / "idf.txt"
    df_path = output / "df.txt"
    tf_dir = output / "tf"
    tfidf_dir = output / "tfidf"

    idf_table = parse_tsv_scores(idf_path)
    if term not in idf_table:
        raise SystemExit(f"{term!r} is not in {idf_path}")

    df_table = parse_df_table(df_path)
    df, owners = df_table.get(term, (0, []))
    idf = idf_table[term]
    expected = math.log(args.n_docs / df) if df else float("nan")

    print(f"term:     {term}")
    print(f"df:       {df} / {args.n_docs}")
    print(f"idf:      {idf:.12f}")
    print(f"ln(N/df): {expected:.12f}   (using --n-docs {args.n_docs})")
    print(f"owners:   {', '.join(owners)}")
    print()

    rows = []
    for path in sorted(tf_dir.glob("*.txt")):
        if path.name.startswith("."):
            continue
        tf_scores = parse_tsv_scores(path)
        if term not in tf_scores:
            continue
        tfidf_scores = parse_tsv_scores(tfidf_dir / path.name)
        tf = tf_scores[term]
        product = tfidf_scores.get(term, float("nan"))
        rows.append((path.name, f"{tf:.12g}", f"{product:.12g}", f"{tf * idf:.12g}"))

    rows.sort(key=lambda row: -float(row[2]))
    if args.top_docs is not None:
        rows = rows[: args.top_docs]

    print(format_table(rows, ("document", "tf", "tfidf file", "tf × idf check")))
    if not rows:
        print("term has an IDF row but no per-document TF row (unexpected)")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
