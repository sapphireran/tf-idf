"""Command-line lab for the personal TF-IDF notebook."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, Optional, Sequence

from .index import CorpusIndex, resolve_corpus
from .rank import rank_query
from .tokenize import tokenize
from .weights import idf, tf as tf_weight, tfidf


def _build_index(args: argparse.Namespace) -> CorpusIndex:
    corpus = getattr(args, "corpus", "tiny")
    tokenizer = getattr(args, "tokenizer", "simple")
    use_stopwords = getattr(args, "stopwords", False)
    directory = resolve_corpus(corpus)
    return CorpusIndex.from_directory(
        directory,
        tokenizer=tokenizer,
        use_stopwords=use_stopwords,
    )


def _print_table(headers: Sequence[str], rows: Iterable[Sequence[object]]) -> None:
    str_rows = [[str(cell) for cell in row] for row in rows]
    widths = [len(h) for h in headers]
    for row in str_rows:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(cell))
    fmt = "  ".join(f"{{:<{w}}}" for w in widths)
    print(fmt.format(*headers))
    print(fmt.format(*("-" * w for w in widths)))
    for row in str_rows:
        print(fmt.format(*row))


def cmd_demo(_args: argparse.Namespace) -> int:
    """Print the fully worked tiny-corpus tables from notebook 04."""
    index = CorpusIndex.from_directory(resolve_corpus("tiny"), tokenizer="simple")
    print(f"tiny corpus  N={index.n_docs}  tokenizer=simple  idf=classic")
    print()
    print("document lengths")
    _print_table(
        ("document", "tokens", "types"),
        [(d.name, d.length, len(d.counts)) for d in index.documents],
    )
    print()
    print("document frequency and classic IDF  (ln)")
    terms = sorted(index.df, key=lambda t: (-index.df[t], t))
    idf_table = index.idf_table("classic")
    _print_table(
        ("term", "df", "idf"),
        [(t, index.df[t], f"{idf_table[t]:.6f}") for t in terms],
    )
    print()
    for doc in index.documents:
        weights = index.weights_for(doc.name, idf_flavor="classic", tf_flavor="normalized")
        ranked = sorted(weights.items(), key=lambda pair: (-pair[1], pair[0]))
        print(f"tf-idf  {doc.name}")
        _print_table(
            ("term", "tf_raw", "tf_norm", "tfidf"),
            [
                (
                    term,
                    doc.counts[term],
                    f"{doc.counts[term] / doc.length:.6f}",
                    f"{weight:.6f}",
                )
                for term, weight in ranked
            ],
        )
        print()
    print("cosine ranks for sample queries")
    for query in ("cat mat", "dog walks", "warm kitchen", "distant telescopes"):
        ranked = rank_query(query, index, scheme="cosine", k=4)
        cells = ",  ".join(f"{row.name}={row.score:.4f}" for row in ranked)
        print(f"  {query!r:24}  {cells}")
    return 0


def cmd_top(args: argparse.Namespace) -> int:
    doc_path = Path(args.doc)
    if doc_path.is_file() and doc_path.parent.name in {"gutenberg", "tiny_corpus"}:
        index = CorpusIndex.from_directory(
            doc_path.parent,
            tokenizer=args.tokenizer,
            use_stopwords=args.stopwords,
        )
        name = doc_path.name
    else:
        index = _build_index(args)
        name = args.doc
    rows = index.top_terms(
        name,
        k=args.k,
        idf_flavor=args.idf,
        tf_flavor=args.tf,
        alpha_only=args.alpha_only,
    )
    print(f"top {args.k}  doc={name}  idf={args.idf}  tf={args.tf}")
    _print_table(("term", "tfidf"), [(term, f"{weight:.8f}") for term, weight in rows])
    return 0


def cmd_rank(args: argparse.Namespace) -> int:
    index = _build_index(args)
    tf_flavor = "bm25" if args.scheme == "bm25" else args.tf
    idf_flavor = "bm25" if args.scheme == "bm25" else args.idf
    ranked = rank_query(
        args.query,
        index,
        scheme=args.scheme,
        idf_flavor=idf_flavor,
        tf_flavor=tf_flavor,
        k=args.k,
    )
    print(
        f"query={args.query!r}  corpus={args.corpus}  "
        f"scheme={args.scheme}  idf={idf_flavor}  N={index.n_docs}"
    )
    _print_table(
        ("rank", "document", "score", "note"),
        [
            (i + 1, row.name, f"{row.score:.8f}", row.note)
            for i, row in enumerate(ranked)
        ],
    )
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    index = _build_index(args)
    flavors = ("classic", "smooth", "probabilistic", "bm25")
    print(f"query={args.query!r}  corpus={args.corpus}  scheme=cosine except bm25 row")
    print()
    for flavor in flavors:
        if flavor == "bm25":
            ranked = rank_query(args.query, index, scheme="bm25", k=args.k)
            label = "bm25"
        else:
            ranked = rank_query(
                args.query,
                index,
                scheme="cosine",
                idf_flavor=flavor,
                tf_flavor="normalized",
                k=args.k,
            )
            label = f"cosine/{flavor}"
        print(label)
        _print_table(
            ("rank", "document", "score"),
            [
                (i + 1, row.name, f"{row.score:.8f}")
                for i, row in enumerate(ranked)
            ],
        )
        print()
    return 0


def cmd_explain(args: argparse.Namespace) -> int:
    doc_path = Path(args.doc)
    if doc_path.is_file():
        index = CorpusIndex.from_directory(
            doc_path.parent,
            tokenizer=args.tokenizer,
            use_stopwords=args.stopwords,
        )
        name = doc_path.name
    else:
        index = _build_index(args)
        name = args.doc
    term = args.term.lower()
    doc = index.document(name)
    df = index.df.get(term, 0)
    count = doc.counts.get(term, 0)
    print(f"term={term!r}  doc={name}  tokenizer={index.tokenizer}")
    print(f"N={index.n_docs}  df={df}  raw_tf={count}  |d|={doc.length}")
    if count == 0:
        print("term does not occur in this document")
    print()
    rows = []
    for flavor in ("classic", "smooth", "probabilistic", "bm25"):
        idf_w = idf(df, index.n_docs, flavor)
        tf_flavor = "bm25" if flavor == "bm25" else "normalized"
        tf_w = tf_weight(
            count,
            doc.length,
            tf_flavor,
            avgdl=index.avgdl,
        )
        rows.append(
            (
                flavor,
                f"{tf_w:.6f}",
                f"{idf_w:.6f}",
                f"{tfidf(tf_w, idf_w):.6f}",
            )
        )
    _print_table(("flavor", "tf", "idf", "product"), rows)
    if term in index.postings:
        print()
        print("also present in:", ", ".join(index.postings[term]))
    return 0


def cmd_corpus_stats(args: argparse.Namespace) -> int:
    index = _build_index(args)
    print(f"corpus={args.corpus}  N={index.n_docs}  avgdl={index.avgdl:.2f}")
    _print_table(
        ("document", "tokens", "types"),
        index.corpus_stats(),
    )
    return 0


def cmd_tokens(args: argparse.Namespace) -> int:
    text = Path(args.doc).read_text(encoding="utf-8", errors="replace")
    tokens, length = tokenize(text, tokenizer=args.tokenizer)
    print(f"doc={args.doc}  tokenizer={args.tokenizer}  tokens={len(tokens)}  length={length}")
    preview = tokens[: args.k]
    print("preview:", " ".join(preview))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python3 -m tfidf",
        description="Personal TF-IDF research lab (stdlib only).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    demo = sub.add_parser("demo", help="worked tiny-corpus tables")
    demo.set_defaults(func=cmd_demo)

    def add_shared(p: argparse.ArgumentParser, *, corpus: bool = True) -> None:
        if corpus:
            p.add_argument("--corpus", default="tiny", help="tiny | gutenberg | directory")
        p.add_argument("--tokenizer", default="simple", choices=("simple", "perl_legacy"))
        p.add_argument("--stopwords", action="store_true")
        p.add_argument("--idf", default="classic", choices=("classic", "smooth", "probabilistic", "bm25"))
        p.add_argument("--tf", default="normalized", choices=("raw", "normalized", "log", "boolean", "bm25"))
        p.add_argument("-k", "--k", type=int, default=10)

    top = sub.add_parser("top", help="highest-weighted terms in one document")
    top.add_argument("--doc", required=True, help="path or document name")
    top.add_argument("--alpha-only", action="store_true")
    add_shared(top, corpus=True)
    top.set_defaults(func=cmd_top)

    rank = sub.add_parser("rank", help="rank documents for a query")
    rank.add_argument("query")
    rank.add_argument("--scheme", default="cosine", choices=("cosine", "dot", "bm25"))
    add_shared(rank)
    rank.set_defaults(func=cmd_rank)

    compare = sub.add_parser("compare", help="same query under several IDF flavors")
    compare.add_argument("query")
    add_shared(compare)
    compare.set_defaults(func=cmd_compare)

    explain = sub.add_parser("explain", help="TF / IDF / product for one term")
    explain.add_argument("term")
    explain.add_argument("--doc", required=True)
    add_shared(explain)
    explain.set_defaults(func=cmd_explain)

    stats = sub.add_parser("corpus-stats", help="token counts per document")
    add_shared(stats)
    stats.set_defaults(func=cmd_corpus_stats)

    tokens = sub.add_parser("tokens", help="preview tokenization of a file")
    tokens.add_argument("--doc", required=True)
    tokens.add_argument("--tokenizer", default="simple", choices=("simple", "perl_legacy"))
    tokens.add_argument("-k", "--k", type=int, default=40)
    tokens.set_defaults(func=cmd_tokens)

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (KeyError, FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
