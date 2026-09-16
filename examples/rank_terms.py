#!/usr/bin/env python3
"""Rank terms in a precomputed TF-IDF table.

Reads the tab-separated files written by tf*idf-product.pl (or by
examples/tiny_tfidf.py) and prints the highest-weighted words.

Examples:

    python3 examples/rank_terms.py carroll-alice
    python3 examples/rank_terms.py --top 8 --all
    python3 examples/rank_terms.py --dir examples/tiny-output/tfidf
"""

from __future__ import annotations

import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DIR = REPO_ROOT / "output" / "tfidf"


def load_weights(path: Path) -> list[tuple[str, float]]:
    rows: list[tuple[str, float]] = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not raw or "\t" not in raw:
            continue
        word, value = raw.split("\t", 1)
        try:
            rows.append((word, float(value)))
        except ValueError:
            continue
    rows.sort(key=lambda item: (-item[1], item[0]))
    return rows


def resolve_table(tfidf_dir: Path, name: str) -> Path:
    candidate = tfidf_dir / name
    if candidate.exists():
        return candidate
    if not name.endswith(".txt"):
        with_suffix = tfidf_dir / f"{name}.txt"
        if with_suffix.exists():
            return with_suffix
    matches = sorted(tfidf_dir.glob(f"*{name}*"))
    matches = [path for path in matches if not path.name.startswith(".")]
    if len(matches) == 1:
        return matches[0]
    available = ", ".join(path.name for path in sorted(tfidf_dir.glob("*.txt")))
    raise SystemExit(
        f"could not resolve {name!r} under {tfidf_dir}\navailable: {available}"
    )


def iter_tables(tfidf_dir: Path, names: list[str], all_docs: bool) -> list[Path]:
    if all_docs or not names:
        return sorted(
            path
            for path in tfidf_dir.iterdir()
            if path.is_file() and not path.name.startswith(".")
        )
    return [resolve_table(tfidf_dir, name) for name in names]


def print_ranking(path: Path, top: int) -> None:
    rows = load_weights(path)
    print(f"== {path.name}  ({len(rows)} terms) ==")
    for index, (word, score) in enumerate(rows[:top], start=1):
        print(f"{index:3}  {score:12.6f}  {word}")
    print()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "documents",
        nargs="*",
        help="document stem or filename (default: all tables in --dir)",
    )
    parser.add_argument(
        "--dir",
        type=Path,
        default=DEFAULT_DIR,
        help="directory of word<TAB>score files (default: output/tfidf)",
    )
    parser.add_argument("--top", type=int, default=15, help="terms to print per document")
    parser.add_argument(
        "--all",
        action="store_true",
        help="rank every table in --dir, ignoring the document list",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.dir.is_dir():
        raise SystemExit(f"missing TF-IDF directory: {args.dir}")
    tables = iter_tables(args.dir, args.documents, args.all)
    if not tables:
        raise SystemExit(f"no TF-IDF tables in {args.dir}")
    for path in tables:
        print_ranking(path, args.top)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
