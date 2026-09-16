#!/usr/bin/env python3
"""Educational TF-IDF that mirrors this repo's Perl pipeline.

Tokenization matches tf-idf-values.pl: lowercase, strip non-alphanumerics,
split on spaces. TF is count / tokens(doc). IDF is ln(N / df) with no
smoothing. N defaults to the number of non-hidden input files (the
definition used by the committed Gutenberg tables), not Perl's $#files.

Example:

    python3 examples/python/tfidf_example.py \\
        --input-dir examples/tiny-corpus/docs \\
        --output-dir /tmp/tiny-tfidf
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from collections import defaultdict
from pathlib import Path


def tokenize_line(line: str) -> list[str]:
    """Replicate the per-line clean in tf-idf-values.pl as closely as Python can."""
    line = line.replace("\r", "").replace("\n", "")
    line = re.sub(r"\s+", " ", line)
    line = line.lower()
    line = re.sub(r"[^a-zA-Z0-9\s]", "", line)
    return [tok for tok in line.split(" ") if tok]


def tokenize_file(path: Path) -> list[str]:
    tokens: list[str] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        tokens.extend(tokenize_line(line))
    return tokens


def iter_documents(input_dir: Path) -> list[Path]:
    files = [p for p in sorted(input_dir.iterdir()) if p.is_file() and not p.name.startswith(".")]
    if not files:
        raise SystemExit(f"no non-hidden files in {input_dir}")
    return files


def compute(input_dir: Path, n_override: int | None = None):
    paths = iter_documents(input_dir)
    per_doc_counts: dict[str, dict[str, int]] = {}
    per_doc_len: dict[str, int] = {}
    df_docs: dict[str, set[str]] = defaultdict(set)

    for path in paths:
        tokens = tokenize_file(path)
        counts: dict[str, int] = defaultdict(int)
        for tok in tokens:
            counts[tok] += 1
        name = path.name
        per_doc_counts[name] = dict(counts)
        per_doc_len[name] = len(tokens)
        for tok in counts:
            df_docs[tok].add(name)

    n = n_override if n_override is not None else len(paths)
    if n <= 0:
        raise SystemExit("N must be positive")

    idf = {}
    for term, docs in df_docs.items():
        df = len(docs)
        idf[term] = math.log(n / df)

    tf: dict[str, dict[str, float]] = {}
    tfidf: dict[str, dict[str, float]] = {}
    for name, counts in per_doc_counts.items():
        length = per_doc_len[name]
        tf[name] = {term: count / length for term, count in counts.items()}
        tfidf[name] = {term: tf[name][term] * idf[term] for term in counts}

    return {
        "n": n,
        "paths": paths,
        "df_docs": df_docs,
        "idf": idf,
        "tf": tf,
        "tfidf": tfidf,
        "lengths": per_doc_len,
    }


def write_tables(result: dict, output_dir: Path) -> None:
    tf_dir = output_dir / "tf"
    tfidf_dir = output_dir / "tfidf"
    tf_dir.mkdir(parents=True, exist_ok=True)
    tfidf_dir.mkdir(parents=True, exist_ok=True)

    for name, weights in result["tf"].items():
        lines = [f"{term}\t{weights[term]}" for term in sorted(weights)]
        (tf_dir / name).write_text("\n".join(lines) + "\n", encoding="utf-8")

    df_rows = ["word \t #docs it exists in \t doc names"]
    for term in sorted(result["df_docs"]):
        docs = sorted(result["df_docs"][term])
        df_rows.append(f"{term}\t{len(docs)}\t{', '.join(docs)}, ")
    (output_dir / "df.txt").write_text("\n".join(df_rows) + "\n", encoding="utf-8")

    idf_lines = [f"{term}\t{result['idf'][term]}" for term in sorted(result["idf"])]
    (output_dir / "idf.txt").write_text("\n".join(idf_lines) + "\n", encoding="utf-8")

    for name, weights in result["tfidf"].items():
        lines = [f"{term}\t{weights[term]}" for term in sorted(weights)]
        (tfidf_dir / name).write_text("\n".join(lines) + "\n", encoding="utf-8")


def top_terms(weights: dict[str, float], k: int = 5) -> list[tuple[str, float]]:
    return sorted(weights.items(), key=lambda item: (-item[1], item[0]))[:k]


def print_summary(result: dict) -> None:
    print(f"N={result['n']} documents, vocabulary={len(result['idf'])} terms")
    for name in sorted(result["tfidf"]):
        heads = ", ".join(
            f"{term}={score:.6f}" for term, score in top_terms(result["tfidf"][name])
        )
        print(f"  {name}: {result['lengths'][name]} tokens; top TF-IDF: {heads}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("examples/tiny-corpus/docs"),
        help="directory of one-document-per-file texts",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("examples/tiny-corpus/expected"),
        help="directory to write tf/, df.txt, idf.txt, tfidf/",
    )
    parser.add_argument(
        "--n",
        type=int,
        default=None,
        help="override collection size N (default: number of input files)",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="compute and print a summary without writing tables",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.input_dir.is_dir():
        print(f"input directory not found: {args.input_dir}", file=sys.stderr)
        return 2
    result = compute(args.input_dir, n_override=args.n)
    if not args.no_write:
        write_tables(result, args.output_dir)
        print(f"wrote tables under {args.output_dir}")
    print_summary(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
