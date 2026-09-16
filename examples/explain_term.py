#!/usr/bin/env python3
"""Explain one term: DF, IDF, TF, and TF-IDF in each document that has it.

Reads the checked-in Gutenberg tables by default:

    python3 examples/explain_term.py alice
    python3 examples/explain_term.py whale
    python3 examples/explain_term.py the

Point --root at examples/tiny-output to inspect the toy corpus.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = REPO_ROOT / "output"


def load_pairs(path: Path) -> dict[str, float]:
    values: dict[str, float] = {}
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not raw or "\t" not in raw:
            continue
        word, value = raw.split("\t", 1)
        try:
            values[word] = float(value)
        except ValueError:
            continue
    return values


def load_df_row(df_path: Path, term: str) -> tuple[int | None, str]:
    for raw in df_path.read_text(encoding="utf-8", errors="replace").splitlines()[1:]:
        cols = raw.split("\t")
        if cols and cols[0] == term:
            count = int(cols[1]) if len(cols) > 1 else 0
            names = cols[2].strip().rstrip(",") if len(cols) > 2 else ""
            return count, names
    return None, ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("term", help="already-tokenized term (lowercase, no punctuation)")
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help="directory that contains df.txt, idf.txt, tf/, tfidf/",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    term = args.term.lower()
    root = args.root
    df_path = root / "df.txt"
    idf_path = root / "idf.txt"
    tf_dir = root / "tf"
    tfidf_dir = root / "tfidf"
    for required in (df_path, idf_path, tf_dir, tfidf_dir):
        if not required.exists():
            raise SystemExit(f"missing {required}")

    df, names = load_df_row(df_path, term)
    idf_table = load_pairs(idf_path)
    idf = idf_table.get(term)
    if df is None or idf is None:
        raise SystemExit(f"{term!r} is not in {root} (try inspect_tokenize.py)")

    n_docs = len([path for path in tf_dir.glob("*.txt") if not path.name.startswith(".")])
    print(f"term : {term}")
    print(f"df   : {df}")
    print(f"idf  : {idf:.12f}   (ln(N/df) as stored; N={n_docs} tables in tf/)")
    if names:
        print(f"docs : {names}")
    print()
    print(f"{'document':<28} {'tf':>12} {'tf-idf':>12}")

    rows: list[tuple[float, str, float, float]] = []
    for path in sorted(tfidf_dir.glob("*.txt")):
        weights = load_pairs(path)
        if term not in weights:
            continue
        tf_path = tf_dir / path.name
        tf_value = load_pairs(tf_path).get(term)
        if tf_value is None:
            continue
        product = tf_value * idf
        rows.append((weights[term], path.name, tf_value, product))

    rows.sort(key=lambda row: (-row[0], row[1]))
    for stored, name, tf_value, product in rows:
        print(f"{name:<28} {tf_value:12.6f} {stored:12.6f}")
        if not math.isclose(stored, product, rel_tol=1e-9, abs_tol=1e-12):
            print(f"  note: stored TF-IDF {stored} != TF*IDF {product}")
    if not rows:
        print("(no per-document rows — df listed files that no longer have TF tables)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
