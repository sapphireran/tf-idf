"""Command-line entry points for the toy tf-idf package."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .model import (
    RAW,
    SMOOTH,
    TfIdfIndex,
    format_score,
    iter_tfidf_dir,
    load_term_table,
    rank_overlap,
)

ROOT = Path(__file__).resolve().parent.parent
TINY = ROOT / "examples" / "tiny_corpus"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tfidf_toy",
        description=(
            "tf-idf on a folder of plain-text documents. Default formula is "
            "normalized term frequency times ln(N/df), matching the Perl "
            "scripts in this repo."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    demo = sub.add_parser(
        "demo",
        help="run the 3-document worked example from examples/tiny_corpus/",
    )
    demo.add_argument(
        "--corpus",
        type=Path,
        default=TINY,
        help="folder of tiny documents (default: examples/tiny_corpus)",
    )
    demo.set_defaults(func=cmd_demo)

    top = sub.add_parser("top", help="print the highest tf-idf tokens per document")
    _add_index_flags(top)
    top.add_argument("--k", type=int, default=12, help="how many terms to print")
    top.add_argument(
        "--only",
        action="append",
        default=[],
        help="filename to include (repeatable). Default: all documents",
    )
    top.set_defaults(func=cmd_top)

    compare = sub.add_parser(
        "compare",
        help="terms that distinguish two documents in the same collection",
    )
    _add_index_flags(compare)
    compare.add_argument("left", help="filename of the first document")
    compare.add_argument("right", help="filename of the second document")
    compare.add_argument("--k", type=int, default=12)
    compare.set_defaults(func=cmd_compare)

    compute = sub.add_parser(
        "compute",
        help="write Perl-style tf/, df.txt, idf.txt, and tfidf/ tables",
    )
    _add_index_flags(compute)
    compute.add_argument(
        "--output",
        type=Path,
        required=True,
        help="output directory (created if needed). Use output_py/ to keep output/ intact",
    )
    compute.set_defaults(func=cmd_compute)

    diff = sub.add_parser(
        "diff-output",
        help="compare two compute trees (for example output/ vs output_py/)",
    )
    diff.add_argument("--left", type=Path, required=True)
    diff.add_argument("--right", type=Path, required=True)
    diff.add_argument("--k", type=int, default=30, help="top-k rank overlap window")
    diff.set_defaults(func=cmd_diff_output)

    return parser


def _add_index_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT / "gutenberg",
        help="folder of source texts (default: gutenberg/)",
    )
    parser.add_argument(
        "--idf",
        choices=(RAW, SMOOTH),
        default=RAW,
        help="raw = ln(N/df) like the Perl scripts; smooth = ln((N+1)/(df+1))+1",
    )
    parser.add_argument(
        "--match-perl-length",
        action="store_true",
        help="count Perl's empty leading split fields in |d| (see docs/tokenization.md)",
    )


def cmd_demo(args: argparse.Namespace) -> int:
    corpus = args.corpus
    print(f"tiny corpus: {corpus}")
    print("idf mode: raw  (ln(N/df); shared terms score 0)")
    print()
    index = TfIdfIndex.from_directory(corpus, idf_mode=RAW)
    _print_index(index, k=6)

    print()
    print("same tokens, smoothed idf  (ln((N+1)/(df+1))+1)")
    print("shared terms are no longer zero; compare with docs/worked-example.md")
    print()
    smoothed = TfIdfIndex.from_directory(corpus, idf_mode=SMOOTH)
    _print_index(smoothed, k=6)
    return 0


def _print_index(index: TfIdfIndex, *, k: int) -> None:
    print(f"N = {index.n_docs} documents, {len(index.idf)} distinct terms")
    print()
    print("document frequency / idf")
    print(f"{'term':<12} {'df':>4}  idf")
    for term in sorted(index.idf, key=lambda t: (index.df[t], t)):
        print(f"{term:<12} {index.df[term]:>4}  {format_score(index.idf[term])}")
    print()
    for doc in index:
        print(f"== {doc.name}  ({doc.length} tokens) ==")
        for term, score in doc.top_terms(k):
            bar = "#" * max(1, int(round(score * 40 / 0.28))) if score else ""
            print(f"  {format_score(score):>18}  {term:<12} {bar}")
        print()


def cmd_top(args: argparse.Namespace) -> int:
    index = _build_index(args)
    names = args.only or [doc.name for doc in index]
    for name in names:
        doc = index.get(name)
        print(f"== {doc.name}  ({doc.length} tokens, idf={index.idf_mode}) ==")
        for term, score in doc.top_terms(args.k):
            print(f"  {format_score(score)}\t{term}")
        print()
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    index = _build_index(args)
    left_rows, right_rows = index.compare(args.left, args.right, k=args.k)
    print(f"collection N={index.n_docs}  idf={index.idf_mode}")
    print(f"distinctive for {args.left}  (score_left - score_right)")
    print(f"{'term':<16} {'left':>14} {'right':>14} {'delta':>14}")
    for term, s_left, s_right, delta in left_rows:
        print(
            f"{term:<16} {format_score(s_left):>14} {format_score(s_right):>14} {format_score(delta):>14}"
        )
    print()
    print(f"distinctive for {args.right}  (score_right - score_left)")
    print(f"{'term':<16} {'right':>14} {'left':>14} {'delta':>14}")
    for term, s_left, s_right, delta in right_rows:
        print(
            f"{term:<16} {format_score(s_right):>14} {format_score(s_left):>14} {format_score(delta):>14}"
        )
    return 0


def cmd_compute(args: argparse.Namespace) -> int:
    index = _build_index(args)
    args.output.mkdir(parents=True, exist_ok=True)
    index.write_legacy_output(args.output)
    print(
        f"wrote tf/, df.txt, idf.txt, tfidf/ for {index.n_docs} documents → {args.output}"
    )
    return 0


def cmd_diff_output(args: argparse.Namespace) -> int:
    left_dir = args.left / "tfidf"
    right_dir = args.right / "tfidf"
    if not left_dir.is_dir() or not right_dir.is_dir():
        print("both --left and --right must contain a tfidf/ directory", file=sys.stderr)
        return 2

    left_tables = dict(iter_tfidf_dir(left_dir))
    right_tables = dict(iter_tfidf_dir(right_dir))
    shared = sorted(set(left_tables) & set(right_tables))
    only_left = sorted(set(left_tables) - set(right_tables))
    only_right = sorted(set(right_tables) - set(left_tables))
    if only_left:
        print(f"only in left: {', '.join(only_left)}")
    if only_right:
        print(f"only in right: {', '.join(only_right)}")

    print(f"{'document':<28} {'max|Δ|':>12} {'mean|Δ|':>12} {'top'+str(args.k)+' overlap':>16}")
    worst_name = ""
    worst_delta = -1.0
    for name in shared:
        left = left_tables[name]
        right = right_tables[name]
        vocab = set(left) | set(right)
        abs_deltas = [abs(left.get(term, 0.0) - right.get(term, 0.0)) for term in vocab]
        max_delta = max(abs_deltas) if abs_deltas else 0.0
        mean_delta = sum(abs_deltas) / len(abs_deltas) if abs_deltas else 0.0
        overlap, _, _ = rank_overlap(left, right, k=args.k)
        print(
            f"{name:<28} {max_delta:12.6g} {mean_delta:12.6g} {overlap:8d}/{args.k}"
        )
        if max_delta > worst_delta:
            worst_delta = max_delta
            worst_name = name

    if shared:
        print()
        print(f"largest max|Δ| was {worst_delta:.6g} in {worst_name}")
        left_idf = args.left / "idf.txt"
        right_idf = args.right / "idf.txt"
        if left_idf.is_file() and right_idf.is_file():
            l_idf = load_term_table(left_idf)
            r_idf = load_term_table(right_idf)
            idf_vocab = set(l_idf) | set(r_idf)
            idf_max = max(abs(l_idf.get(t, 0.0) - r_idf.get(t, 0.0)) for t in idf_vocab)
            print(f"idf.txt max|Δ| = {idf_max:.6g} across {len(idf_vocab)} terms")
    return 0


def _build_index(args: argparse.Namespace) -> TfIdfIndex:
    return TfIdfIndex.from_directory(
        args.input,
        idf_mode=args.idf,
        match_perl_length=args.match_perl_length,
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))
