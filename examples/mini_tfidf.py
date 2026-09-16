#!/usr/bin/env python3
"""Score a folder of tiny documents with the same TF-IDF product as the Perl.

Examples:

    python3 examples/mini_tfidf.py examples/mini_corpus/three_docs
    python3 examples/mini_tfidf.py examples/mini_corpus/literary_snippets --top 8
    python3 examples/mini_tfidf.py examples/mini_corpus/three_docs --variant smooth
    python3 examples/mini_tfidf.py examples/mini_corpus/three_docs --variant log_tf
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from tfidf_lib import build_model, format_table, read_documents  # noqa: E402


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "corpus",
        type=Path,
        help="Directory of .txt documents (see examples/mini_corpus/)",
    )
    parser.add_argument(
        "--variant",
        choices=("raw", "smooth", "log_tf", "prob"),
        default="raw",
        help="raw = Perl-compatible; others are teaching variants",
    )
    parser.add_argument(
        "--n-docs",
        type=int,
        default=None,
        help="Override N (default: number of files actually read)",
    )
    parser.add_argument("--top", type=int, default=None, help="Show only the top K terms per document")
    return parser.parse_args(argv)


def modes_for_variant(variant: str) -> tuple[str, str]:
    if variant == "raw":
        return "proportion", "raw"
    if variant == "smooth":
        return "proportion", "smooth"
    if variant == "prob":
        return "proportion", "prob"
    if variant == "log_tf":
        return "log", "raw"
    raise ValueError(variant)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    corpus = args.corpus
    if not corpus.is_dir():
        raise SystemExit(f"not a directory: {corpus}")

    tf_mode, idf_mode = modes_for_variant(args.variant)
    texts = read_documents(corpus)
    model = build_model(texts, n_docs=args.n_docs, tf_mode=tf_mode, idf_mode=idf_mode)

    print(f"corpus:   {corpus}")
    print(f"docs:     {len(texts)}  N={model.n_docs}")
    print(f"vocab:    {len(model.vocabulary)}")
    print(f"tf mode:  {model.tf_mode}")
    print(f"idf mode: {model.idf_mode}")
    print()

    idf_rows = [
        (term, model.df[term], f"{model.idf[term]:.12f}")
        for term in model.vocabulary
    ]
    print("Collection IDF")
    print(format_table(idf_rows, ("term", "df", "idf")))
    print()

    for name in sorted(model.tfidf):
        ranked = model.ranked(name, top=args.top)
        rows = [
            (
                term,
                model.documents[name].count(term),
                f"{model.tf[name][term]:.12f}",
                f"{model.idf[term]:.12f}",
                f"{score:.12f}",
            )
            for term, score in ranked
        ]
        print(f"# {name}  ({len(model.documents[name])} tokens)")
        print(format_table(rows, ("term", "count", "tf", "idf", "tfidf")))
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
