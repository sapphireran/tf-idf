#!/usr/bin/env python3
"""Show one term's tf, idf, df, and per-document tf-idf.

Usage (from the repo root):
    python3 examples/term_report.py alice
    python3 examples/term_report.py whale --top 8
    python3 examples/term_report.py haue the macbeth
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TF_DIR = ROOT / "output" / "tf"
TFIDF_DIR = ROOT / "output" / "tfidf"
IDF_PATH = ROOT / "output" / "idf.txt"
DF_PATH = ROOT / "output" / "df.txt"


def load_two_column(path: Path) -> dict[str, str]:
    table = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw or raw.startswith("word \t"):
            continue
        term, value, *_rest = raw.split("\t")
        table[term] = value
    return table


def load_df_files() -> dict[str, tuple[int, str]]:
    """term -> (df integer, filename blob)."""
    out: dict[str, tuple[int, str]] = {}
    for raw in DF_PATH.read_text(encoding="utf-8").splitlines():
        if not raw or raw.startswith("word \t"):
            continue
        parts = raw.split("\t")
        if len(parts) < 2:
            continue
        term = parts[0]
        try:
            df = int(parts[1])
        except ValueError:
            continue
        names = parts[2].strip().rstrip(",") if len(parts) > 2 else ""
        out[term] = (df, names)
    return out


def term_column(directory: Path, term: str) -> list[tuple[str, float]]:
    rows = []
    for path in sorted(directory.glob("*.txt")):
        weights = load_two_column(path)
        if term in weights:
            rows.append((path.name, float(weights[term])))
    rows.sort(key=lambda item: (-item[1], item[0]))
    return rows


def report(term: str, top: int) -> None:
    idf_table = load_two_column(IDF_PATH)
    df_table = load_df_files()

    print(f"term: {term!r}")
    if term not in idf_table:
        print("  not present in output/idf.txt (never occurred in the snapshot corpus)")
        return

    idf = float(idf_table[term])
    df, names = df_table.get(term, (-1, ""))
    print(f"  idf: {idf:.12g}")
    print(f"  df:  {df}  {names}")
    if idf == 0:
        print("  note: idf 0 — this term appears in every document; tf-idf is 0 everywhere")

    tfidf_rows = term_column(TFIDF_DIR, term)
    tf_map = {name: score for name, score in term_column(TF_DIR, term)}

    print()
    print(f"  {'document':<32} {'tf':>14}  {'tf-idf':>14}")
    shown = tfidf_rows[:top] if top >= 0 else tfidf_rows
    for name, tfidf in shown:
        tf = tf_map.get(name, float("nan"))
        print(f"  {name:<32} {tf:14.12g}  {tfidf:14.12g}")
    hidden = len(tfidf_rows) - len(shown)
    if hidden > 0:
        print(f"  … {hidden} more document(s) with a non-zero occurrence")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("terms", nargs="+", help="Lowercase terms (as stored in output/)")
    parser.add_argument("--top", type=int, default=18, help="Documents to list per term")
    args = parser.parse_args()

    if not IDF_PATH.is_file():
        print("missing output/idf.txt — run from the repo root", file=sys.stderr)
        return 2

    for i, term in enumerate(args.terms):
        if i:
            print()
        report(term.lower(), args.top)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
