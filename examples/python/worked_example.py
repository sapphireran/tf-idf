#!/usr/bin/env python3
"""Print every cell of the three-sentence classroom example."""

from __future__ import annotations

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from tfidf_lab import build_worked_example


def main() -> int:
    example = build_worked_example()
    assert example.index is not None
    print("Documents")
    for doc in example.documents:
        print(f"  {doc.name}: {doc.text!r} -> {doc.tokens}")
    print()
    print(f"N = {example.index.n_documents}")
    print()
    print(f"{'doc':10s} {'term':8s} {'c':>3s} {'len':>3s} {'tf':>10s} {'df':>3s} {'idf':>10s} {'tfidf':>10s}")
    for row in example.rows:
        print(
            f"{row.document:10s} {row.term:8s} {row.count:3d} {row.length:3d} "
            f"{row.tf:10.6f} {row.df:3d} {row.idf:10.6f} {row.tfidf:10.6f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
