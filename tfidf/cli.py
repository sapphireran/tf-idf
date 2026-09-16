"""Command-line entry point: ``python3 -m tfidf <command>``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .compute import build_index, pairwise_cosine, score_query
from .io_tsv import load_existing_tfidf_dir, write_pipeline_output
from .report import render_corpus_report, render_existing_top_terms


def _add_index_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--idf",
        choices=("raw", "smooth"),
        default="raw",
        help="raw = log(N/df) like the Perl scripts; smooth = sklearn-shaped IDF",
    )
    parser.add_argument(
        "--perl-compat",
        action="store_true",
        help="count leading empty split fields in the TF denominator",
    )
    parser.add_argument(
        "--glob",
        default="*.txt",
        dest="pattern",
        help="file glob inside input_dir (default: *.txt, so README.md is skipped)",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tfidf",
        description=(
            "Educational TF-IDF toolkit for the personal Gutenberg toy corpus "
            "in this repository."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    compute = sub.add_parser("compute", help="write tf/, idf.txt, df.txt, and tfidf/")
    compute.add_argument("input_dir", type=Path, help="directory of plain-text documents")
    compute.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        required=True,
        help="directory to create (tf/ and tfidf/ are created inside it)",
    )
    _add_index_flags(compute)

    report = sub.add_parser("report", help="print a markdown TF-IDF report")
    report.add_argument("input_dir", type=Path)
    report.add_argument("-n", "--n", "--top", type=int, default=8, dest="top_n")
    report.add_argument("-q", "--query", default=None, help="optional ranking query")
    _add_index_flags(report)

    top = sub.add_parser("top", help="print top terms for each document in a corpus")
    top.add_argument("input_dir", type=Path)
    top.add_argument("-n", "--n", "--top", type=int, default=10, dest="top_n")
    _add_index_flags(top)

    top_tsv = sub.add_parser(
        "top-tsv",
        help="rank terms in already-computed TF-IDF TSV files (e.g. output/tfidf)",
    )
    top_tsv.add_argument("tfidf_dir", type=Path)
    top_tsv.add_argument("-n", "--n", "--top", type=int, default=10, dest="top_n")

    query = sub.add_parser("query", help="rank documents against a free-text query")
    query.add_argument("input_dir", type=Path)
    query.add_argument("query_text", help="query string, e.g. 'sperm whale boat'")
    _add_index_flags(query)

    similar = sub.add_parser("similar", help="pairwise cosine similarity of a corpus")
    similar.add_argument("input_dir", type=Path)
    _add_index_flags(similar)

    return parser


def _index_from_args(args: argparse.Namespace):
    return build_index(
        args.input_dir,
        idf_mode=args.idf,
        perl_compat=args.perl_compat,
        pattern=args.pattern,
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "compute":
        index = _index_from_args(args)
        write_pipeline_output(index, args.output_dir)
        print(
            f"wrote {index.n_documents} documents, "
            f"{len(index.idf)} terms -> {args.output_dir}",
            file=sys.stderr,
        )
        return 0

    if args.command == "report":
        index = _index_from_args(args)
        sys.stdout.write(
            render_corpus_report(index, top_n=args.top_n, query=args.query)
        )
        return 0

    if args.command == "top":
        index = _index_from_args(args)
        for doc in index.documents:
            print(f"# {doc.name}")
            for term, score in doc.top_terms(args.top_n):
                print(f"{score:.8f}\t{term}")
            print()
        return 0

    if args.command == "top-tsv":
        tables = load_existing_tfidf_dir(args.tfidf_dir)
        sys.stdout.write(render_existing_top_terms(tables, top_n=args.top_n))
        return 0

    if args.command == "query":
        index = _index_from_args(args)
        for name, score in score_query(index, args.query_text):
            print(f"{score:.4f}\t{name}")
        return 0

    if args.command == "similar":
        index = _index_from_args(args)
        for left, right, score in pairwise_cosine(index):
            print(f"{score:.4f}\t{left}\t{right}")
        return 0

    parser.error(f"unhandled command {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
