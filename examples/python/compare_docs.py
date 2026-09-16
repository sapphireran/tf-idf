#!/usr/bin/env python3
"""Compare two or more scored documents with cosine similarity."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from tfidf_lab import (
    build_index,
    cosine_similarity,
    load_documents,
    read_term_weights,
)


def compare_from_directory(docs_dir: Path, variant: str) -> None:
    index = build_index(load_documents(docs_dir), variant=variant)
    names = [doc.name for doc in index.documents]
    print(f"scored {len(names)} documents with variant={variant}")
    print()
    for i, left in enumerate(names):
        for right in names[i + 1 :]:
            score = index.cosine(left, right)
            print(f"{score:.4f}  {left}  ~  {right}")
    print()
    print("strongest shared terms for each pair (by min tf-idf)")
    for i, left in enumerate(names):
        for right in names[i + 1 :]:
            shared = set(index.vector(left)) & set(index.vector(right))
            ranked = sorted(
                (
                    (
                        term,
                        min(index.vector(left)[term], index.vector(right)[term]),
                    )
                    for term in shared
                ),
                key=lambda item: (-item[1], item[0]),
            )[:6]
            pretty = ", ".join(f"{term}={score:.4f}" for term, score in ranked)
            print(f"  {left} ~ {right}: {pretty}")


def compare_weight_files(paths: list[Path]) -> None:
    vectors = {path.name: read_term_weights(path) for path in paths}
    names = list(vectors)
    for i, left in enumerate(names):
        for right in names[i + 1 :]:
            score = cosine_similarity(vectors[left], vectors[right])
            print(f"{score:.4f}  {left}  ~  {right}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="a docs/ directory, or two or more TF-IDF TSV files",
    )
    parser.add_argument(
        "--variant",
        choices=("repo", "log_tf", "smooth_idf"),
        default="repo",
    )
    args = parser.parse_args()

    if len(args.paths) == 1 and args.paths[0].is_dir():
        compare_from_directory(args.paths[0], args.variant)
        return 0
    if all(path.is_file() for path in args.paths):
        compare_weight_files(args.paths)
        return 0
    print("pass one document directory or two-plus TSV files", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
