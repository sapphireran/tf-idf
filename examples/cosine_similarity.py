#!/usr/bin/env python3
"""Pairwise cosine similarity on TF-IDF vectors.

Mini corpus (recomputes scores):

    python3 examples/cosine_similarity.py --corpus examples/mini_corpus/three_docs

Committed Gutenberg tables (reads output/tfidf, no Perl rerun):

    python3 examples/cosine_similarity.py --from-output output/tfidf
    python3 examples/cosine_similarity.py --from-output output/tfidf --top-pairs 12
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from tfidf_lib import (  # noqa: E402
    build_model,
    cosine,
    format_table,
    pairwise_cosine,
    parse_tsv_scores,
    read_documents,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--corpus", type=Path, help="Folder of raw .txt documents")
    source.add_argument(
        "--from-output",
        type=Path,
        help="Folder of already-scored TSV files (output/tfidf)",
    )
    parser.add_argument("--top-pairs", type=int, default=None, help="Show only the most similar pairs")
    parser.add_argument(
        "--variant",
        choices=("raw", "smooth", "log_tf", "prob"),
        default="raw",
        help="Only used with --corpus",
    )
    return parser.parse_args(argv)


def load_output_vectors(directory: Path) -> tuple[list[str], dict[str, list[float]]]:
    scores = {}
    vocab: set[str] = set()
    for path in sorted(directory.glob("*.txt")):
        if path.name.startswith("."):
            continue
        table = parse_tsv_scores(path)
        scores[path.name] = table
        vocab.update(table)
    names = sorted(scores)
    space = sorted(vocab)
    vectors = {
        name: [scores[name].get(term, 0.0) for term in space]
        for name in names
    }
    return names, vectors


def pairs_from_vectors(names: list[str], vectors: dict[str, list[float]]) -> list[tuple[str, str, float]]:
    pairs = []
    for i, left in enumerate(names):
        for right in names[i + 1 :]:
            pairs.append((left, right, cosine(vectors[left], vectors[right])))
    pairs.sort(key=lambda row: (-row[2], row[0], row[1]))
    return pairs


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.corpus is not None:
        from mini_tfidf import modes_for_variant

        tf_mode, idf_mode = modes_for_variant(args.variant)
        model = build_model(read_documents(args.corpus), tf_mode=tf_mode, idf_mode=idf_mode)
        pairs = pairwise_cosine(model)
        print(f"source: recomputed from {args.corpus}  variant={args.variant}  dim={len(model.vocabulary)}")
    else:
        if not args.from_output.is_dir():
            raise SystemExit(f"not a directory: {args.from_output}")
        names, vectors = load_output_vectors(args.from_output)
        pairs = pairs_from_vectors(names, vectors)
        dim = len(next(iter(vectors.values()))) if vectors else 0
        print(f"source: {args.from_output}  docs={len(names)}  dim={dim}")

    if args.top_pairs is not None:
        pairs = pairs[: args.top_pairs]

    rows = [(left, right, f"{score:.6f}") for left, right, score in pairs]
    print(format_table(rows, ("left", "right", "cosine")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
