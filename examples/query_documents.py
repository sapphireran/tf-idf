#!/usr/bin/env python3
"""Score documents for a bag-of-words query using precomputed TF-IDF.

For each query term, look up that term's TF-IDF weight in a document and
sum the hits. Terms that never appear in a document contribute 0.

This is the same ranking idea as "which book on the shelf is most about
these words?", using the tables already sitting in output/tfidf/.

Examples:

    python3 examples/query_documents.py alice gryphon hatter
    python3 examples/query_documents.py whale ahab pequod
    python3 examples/query_documents.py --dir examples/tiny-output/tfidf tea rabbit
"""

from __future__ import annotations

import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DIR = REPO_ROOT / "output" / "tfidf"


def load_weights(path: Path) -> dict[str, float]:
    weights: dict[str, float] = {}
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not raw or "\t" not in raw:
            continue
        word, value = raw.split("\t", 1)
        try:
            weights[word] = float(value)
        except ValueError:
            continue
    return weights


def score_document(weights: dict[str, float], query: list[str]) -> tuple[float, list[str]]:
    hits: list[str] = []
    total = 0.0
    for term in query:
        value = weights.get(term)
        if value:
            total += value
            hits.append(term)
    return total, hits


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "terms",
        nargs="+",
        help="query terms, already tokenized the same way as the tables",
    )
    parser.add_argument(
        "--dir",
        type=Path,
        default=DEFAULT_DIR,
        help="directory of word<TAB>score files (default: output/tfidf)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=8,
        help="how many ranked documents to print",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.dir.is_dir():
        raise SystemExit(f"missing TF-IDF directory: {args.dir}")

    query = [term.lower() for term in args.terms]
    ranked: list[tuple[float, str, list[str]]] = []
    for path in sorted(args.dir.iterdir()):
        if not path.is_file() or path.name.startswith("."):
            continue
        total, hits = score_document(load_weights(path), query)
        ranked.append((total, path.name, hits))

    ranked.sort(key=lambda row: (-row[0], row[1]))
    print("query:", " ".join(query))
    print()
    for index, (total, name, hits) in enumerate(ranked[: args.top], start=1):
        hit_label = ",".join(hits) if hits else "-"
        print(f"{index:3}  {total:10.6f}  {name:28}  hits={hit_label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
