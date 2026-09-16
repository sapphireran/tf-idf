"""Command-line query desk for the personal Gutenberg TF-IDF toy."""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

from .index import ROOT, Index, build_index, load_committed_index, write_index_tables
from .query import compare_rankings, explain, rank
from .tables import load_tf_tsv

FIELD_NOTES = ROOT / "examples" / "field-notes" / "texts"
FIELD_NOTES_EXPECTED = ROOT / "examples" / "field-notes" / "expected"
GUTENBERG = ROOT / "gutenberg"
OUTPUT = ROOT / "output"


def _index_from_args(args: argparse.Namespace) -> Index:
    variant = getattr(args, "variant", "classic") or "classic"
    if getattr(args, "from_committed", False):
        return load_committed_index(OUTPUT, variant=variant)
    corpus = getattr(args, "corpus", None)
    corpus_dir = Path(corpus) if corpus else GUTENBERG
    n_mode = getattr(args, "n_mode", "texts") or "texts"
    return build_index(corpus_dir, variant=variant, n_mode=n_mode)


def _print_hits(hits, *, limit: int) -> None:
    width = max((len(hit.name) for hit in hits[:limit]), default=4)
    print(f"{'doc':<{width}}  score")
    print(f"{'-' * width}  -----")
    for hit in hits[:limit]:
        print(f"{hit.name:<{width}}  {hit.score:.6f}")


def cmd_rank(args: argparse.Namespace) -> int:
    index = _index_from_args(args)
    hits = rank(args.query, index, score=args.score, top=args.top)
    print(f"N={index.n}  variant={index.variant}  score={args.score}  query={args.query!r}")
    _print_hits(hits, limit=args.top)
    return 0


def cmd_explain(args: argparse.Namespace) -> int:
    index = _index_from_args(args)
    hits = rank(args.query, index, score="cosine", top=1)
    doc_name = args.doc or (hits[0].name if hits else None)
    if not doc_name:
        print("no documents", file=sys.stderr)
        return 1
    cosine_score, rows = explain(args.query, index, doc_name, top=args.top)
    print(f"doc={doc_name}  cosine={cosine_score:.6f}  query={args.query!r}")
    print(f"{'term':<16}  {'q_tfidf':>12}  {'d_tfidf':>12}  {'product':>12}")
    for row in rows:
        print(
            f"{row.term:<16}  {row.query_weight:12.6f}  {row.doc_weight:12.6f}  {row.product:12.6f}"
        )
    return 0


def cmd_top(args: argparse.Namespace) -> int:
    path = OUTPUT / "tfidf" / args.doc
    if not path.exists():
        print(f"missing gold file: {path}", file=sys.stderr)
        return 1
    weights = load_tf_tsv(path)
    ranked = sorted(weights.items(), key=lambda item: (-item[1], item[0]))[: args.n]
    print(f"gold TF-IDF  {args.doc}  N_terms={len(weights)}")
    for term, value in ranked:
        print(f"{value:.6f}\t{term}")
    return 0


def cmd_field_notes(args: argparse.Namespace) -> int:
    index = build_index(FIELD_NOTES, variant="classic", n_mode="texts")
    if args.write_expected:
        write_index_tables(index, FIELD_NOTES_EXPECTED)
        print(f"wrote expected tables under {FIELD_NOTES_EXPECTED}")
    print(f"field notes  N={index.n}  docs={', '.join(sorted(index.docs))}")
    query = args.query or "cairn moraine icefall"
    hits = rank(query, index, score="cosine", top=4)
    print(f"query={query!r}")
    _print_hits(hits, limit=4)
    winner = hits[0].name if hits else ""
    if winner:
        _, rows = explain(query, index, winner, top=6)
        print(f"top contributions in {winner}:")
        for row in rows[:6]:
            print(f"  {row.term:12} {row.product:.6f}")
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    index = _index_from_args(args)
    variants = [part.strip() for part in args.variants.split(",") if part.strip()]
    grouped = compare_rankings(args.query, index, variants, top=args.top)
    print(f"query={args.query!r}")
    for variant, hits in grouped.items():
        print(f"\n[{variant}]")
        _print_hits(hits, limit=args.top)
    return 0


def _almost(left: float, right: float, tol: float = 1e-12) -> bool:
    return abs(left - right) <= tol


def cmd_self_test(args: argparse.Namespace) -> int:
    """Retokenize Gutenberg and diff a sample against output/."""
    built = build_index(GUTENBERG, variant="classic", n_mode="texts")
    gold_idf = load_tf_tsv(OUTPUT / "idf.txt")
    failures: list[str] = []

    if built.n != 18:
        failures.append(f"N={built.n}, expected 18")

    hapax = max(gold_idf.values())
    if not _almost(hapax, math.log(18)):
        failures.append(f"gold hapax idf {hapax} != ln(18)")

    sample_terms = ["alice", "whale", "macb", "thel", "the", "gryphon", "emma"]
    for term in sample_terms:
        if term not in gold_idf or term not in built.idf:
            failures.append(f"missing idf for {term}")
            continue
        if not _almost(built.idf[term], gold_idf[term], 1e-12):
            failures.append(
                f"idf[{term}] built={built.idf[term]!r} gold={gold_idf[term]!r}"
            )

    alice = "carroll-alice.txt"
    gold_tf = load_tf_tsv(OUTPUT / "tf" / alice)
    gold_tfidf = load_tf_tsv(OUTPUT / "tfidf" / alice)
    built_tf = built.docs[alice].tf
    built_tfidf = built.docs[alice].tfidf
    if set(built_tf) != set(gold_tf):
        failures.append(
            f"alice TF key mismatch extra={set(built_tf)-set(gold_tf)} "
            f"missing={set(gold_tf)-set(built_tf)}"
        )
    max_tf = max(abs(built_tf[t] - gold_tf[t]) for t in gold_tf)
    max_tfidf = max(abs(built_tfidf[t] - gold_tfidf[t]) for t in gold_tfidf)
    if max_tf > 1e-14:
        failures.append(f"alice max|Δ tf|={max_tf}")
    if max_tfidf > 1e-14:
        failures.append(f"alice max|Δ tfidf|={max_tfidf}")

    hits = rank("white whale pequod ahab", built, score="cosine", top=1)
    if not hits or hits[0].name != "melville-moby_dick.txt":
        failures.append(f"whale query winner={hits[:1]!r}")

    field = build_index(FIELD_NOTES, variant="classic", n_mode="texts")
    for query, expected in (
        ("cairn moraine icefall", "glacier-cairn.txt"),
        ("chase quoins tympan", "letterpress-proof.txt"),
        ("stilling datum slack", "tide-gauge.txt"),
        ("voucher blotters silica", "herbarium-press.txt"),
    ):
        winner = rank(query, field, score="cosine", top=1)[0].name
        if winner != expected:
            failures.append(f"field-notes {query!r} -> {winner}, expected {expected}")

    if failures:
        print("self-test FAILED")
        for item in failures:
            print(f"  - {item}")
        return 1
    print("self-test ok")
    print(f"  Gutenberg N={built.n}  terms={len(built.idf)}  alice max|Δ tf|={max_tf:.2e}")
    print(f"  alice max|Δ tfidf|={max_tfidf:.2e}")
    print("  field-notes rankings match the four themes")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="querydesk",
        description="Personal query desk for the 2012 Gutenberg TF-IDF toy.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    def add_index_flags(p: argparse.ArgumentParser) -> None:
        p.add_argument("--corpus", type=str, default=str(GUTENBERG))
        p.add_argument("--from-committed", action="store_true")
        p.add_argument("--variant", default="classic")
        p.add_argument("--n-mode", choices=("texts", "perl-last-index"), default="texts")
        p.add_argument("--top", type=int, default=8)

    rank_p = sub.add_parser("rank", help="rank Gutenberg (or --corpus) for a query")
    rank_p.add_argument("query")
    rank_p.add_argument("--score", choices=("cosine", "dot", "bm25"), default="cosine")
    add_index_flags(rank_p)
    rank_p.set_defaults(func=cmd_rank)

    exp_p = sub.add_parser("explain", help="term contributions for a hit")
    exp_p.add_argument("query")
    exp_p.add_argument("--doc", default=None)
    add_index_flags(exp_p)
    exp_p.set_defaults(func=cmd_explain)

    top_p = sub.add_parser("top", help="highest gold TF-IDF terms in one file")
    top_p.add_argument("--doc", required=True)
    top_p.add_argument("--n", type=int, default=12)
    top_p.set_defaults(func=cmd_top)

    fn_p = sub.add_parser("field-notes", help="rank the four-note tiny corpus")
    fn_p.add_argument("--query", default=None)
    fn_p.add_argument("--write-expected", action="store_true")
    fn_p.set_defaults(func=cmd_field_notes)

    cmp_p = sub.add_parser("compare", help="classic vs smooth vs bm25 rankings")
    cmp_p.add_argument("query")
    cmp_p.add_argument("--variants", default="classic,smooth,bm25")
    add_index_flags(cmp_p)
    cmp_p.set_defaults(func=cmd_compare)

    st_p = sub.add_parser("self-test", help="diff tokenizer/weights against gold tables")
    st_p.set_defaults(func=cmd_self_test)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))
