#!/usr/bin/env python3
"""Score the tiny personal corpus and write TSV tables plus a summary."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from tfidf_lab import build_index, load_documents, write_index


def summarize(index, limit: int = 8) -> str:
    lines = [
        f"variant: {index.variant}",
        f"documents: {index.n_documents}",
        f"vocabulary: {len(index.vocabulary())}",
        "",
        "Top TF-IDF terms per document",
    ]
    for doc in index.documents:
        lines.append(f"  {doc.name} ({doc.length} tokens)")
        for term, score in index.scored[doc.name].top_terms(limit):
            lines.append(f"    {term:16s} {score:.6f}")
        lines.append("")
    lines.append("Pairwise cosine similarity (TF-IDF vectors)")
    names = [doc.name for doc in index.documents]
    header = "                " + " ".join(f"{name[:14]:>14s}" for name in names)
    lines.append(header)
    for left in names:
        row = [f"{left[:14]:14s}"]
        for right in names:
            row.append(f"{index.cosine(left, right):14.3f}")
        lines.append(" ".join(row))
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--docs",
        type=Path,
        default=ROOT / "examples" / "tiny_corpus" / "docs",
        help="directory of UTF-8 text files",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "examples" / "tiny_corpus" / "expected",
        help="directory for TSV tables",
    )
    parser.add_argument(
        "--variant",
        choices=("repo", "log_tf", "smooth_idf"),
        default="repo",
    )
    parser.add_argument("--top", type=int, default=8)
    args = parser.parse_args()

    documents = load_documents(args.docs)
    index = build_index(documents, variant=args.variant)
    write_index(index, args.out)
    summary = summarize(index, limit=args.top)
    (args.out / "summary.txt").write_text(summary, encoding="utf-8")
    print(summary, end="")
    print(f"\nwrote tables to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
