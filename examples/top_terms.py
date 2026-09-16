#!/usr/bin/env python3
"""Rank checked-in TF-IDF tables for the personal Gutenberg toy project.

Read from output/tfidf/ (and optionally output/tf/ + output/idf.txt) and
print the highest-scoring terms. Parses floats in Python so scientific
notation ranks correctly — unlike `sort -n` on many systems.

Run from the repository root:

    python3 examples/top_terms.py --n 10
    python3 examples/top_terms.py --doc carroll-alice --n 20 --show-tf --show-idf
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "output"
TFIDF_DIR = OUTPUT / "tfidf"
TF_DIR = OUTPUT / "tf"
IDF_PATH = OUTPUT / "idf.txt"


def load_term_scores(path: Path) -> dict[str, float]:
    scores: dict[str, float] = {}
    with path.open(encoding="utf-8", errors="replace") as handle:
        for raw in handle:
            line = raw.rstrip("\n")
            if not line or line.startswith("word"):
                continue
            term, sep, rest = line.partition("\t")
            if not sep:
                continue
            value_str = rest.split("\t", 1)[0].strip()
            try:
                scores[term] = float(value_str)
            except ValueError:
                continue
    return scores


def load_idf() -> dict[str, float]:
    if not IDF_PATH.is_file():
        return {}
    return load_term_scores(IDF_PATH)


def normalize_doc_name(name: str) -> str:
    name = name.strip()
    if not name.endswith(".txt"):
        name += ".txt"
    return name


def list_tfidf_docs() -> list[str]:
    return sorted(p.name for p in TFIDF_DIR.glob("*.txt"))


def ranked_terms(tfidf: dict[str, float]) -> list[tuple[str, float]]:
    return sorted(tfidf.items(), key=lambda item: (-item[1], item[0]))


def format_row(
    rank: int,
    term: str,
    tfidf: float,
    tf_value: float | None,
    idf_value: float | None,
    width: int,
) -> str:
    parts = [f"{rank:4d}  {term:<{width}}  {tfidf:.8g}"]
    if tf_value is not None:
        parts.append(f"  tf={tf_value:.8g}")
    if idf_value is not None:
        parts.append(f"  idf={idf_value:.8g}")
    return "".join(parts)


def print_doc(
    doc: str,
    n: int,
    show_tf: bool,
    show_idf: bool,
    idf: dict[str, float],
    min_score: float,
    skip_digits: bool,
) -> int:
    tfidf_path = TFIDF_DIR / doc
    if not tfidf_path.is_file():
        print(f"error: no TF-IDF table for {doc}", file=sys.stderr)
        return 2

    tfidf = load_term_scores(tfidf_path)
    tf_scores = load_term_scores(TF_DIR / doc) if show_tf else {}
    rows = ranked_terms(tfidf)
    if skip_digits:
        rows = [(t, s) for t, s in rows if not t.isdigit()]
    rows = [(t, s) for t, s in rows if s >= min_score]

    width = max((len(term) for term, _ in rows[:n]), default=4)
    width = max(width, 8)
    print(f"# {doc}  ({len(tfidf)} terms, showing {min(n, len(rows))})")
    for rank, (term, score) in enumerate(rows[:n], start=1):
        print(
            format_row(
                rank,
                term,
                score,
                tf_scores.get(term) if show_tf else None,
                idf.get(term) if show_idf else None,
                width,
            )
        )
    print()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Rank terms in the checked-in output/tfidf tables."
    )
    parser.add_argument(
        "--doc",
        action="append",
        dest="docs",
        help="Book stem or filename (repeatable). Default: every book.",
    )
    parser.add_argument("--n", type=int, default=10, help="Terms per book (default 10).")
    parser.add_argument(
        "--show-tf",
        action="store_true",
        help="Also print the matching output/tf value when present.",
    )
    parser.add_argument(
        "--show-idf",
        action="store_true",
        help="Also print the matching output/idf.txt value when present.",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=0.0,
        help="Drop terms with TF-IDF below this value.",
    )
    parser.add_argument(
        "--skip-digits",
        action="store_true",
        help="Hide terms that are only digits (useful for bible-kjv).",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Print available document names and exit.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not TFIDF_DIR.is_dir():
        print(f"error: missing {TFIDF_DIR}", file=sys.stderr)
        return 2

    available = list_tfidf_docs()
    if args.list:
        for name in available:
            print(name)
        return 0

    if args.n < 1:
        print("error: --n must be >= 1", file=sys.stderr)
        return 2

    docs = [normalize_doc_name(d) for d in args.docs] if args.docs else available
    unknown = [d for d in docs if d not in available]
    if unknown:
        print("error: unknown document(s): " + ", ".join(unknown), file=sys.stderr)
        print("use --list to see names", file=sys.stderr)
        return 2

    idf = load_idf() if args.show_idf else {}
    status = 0
    for doc in docs:
        status = max(
            status,
            print_doc(
                doc,
                args.n,
                args.show_tf,
                args.show_idf,
                idf,
                args.min_score,
                args.skip_digits,
            ),
        )
    return status


if __name__ == "__main__":
    sys.exit(main())
