"""Command-line surface for the personal shelf-units study kit."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .commonplace import load_commonplace
from .index import Document, TfIdfIndex
from .retrieve import rank_passages
from .split_bible import expected_book_ids, load_bible
from .split_chapters import SPLITTERS, load_chapters
from .split_speakers import ALIASES, load_speakers

REPO_ROOT = Path(__file__).resolve().parents[1]
GUTENBERG = REPO_ROOT / "gutenberg"


def _print_top(index: TfIdfIndex, k: int, limit_docs: int | None = None) -> None:
    docs = index.documents
    if limit_docs is not None:
        docs = docs[:limit_docs]
    for doc in docs:
        terms = index.top_terms(doc.doc_id, k=k)
        pretty = ", ".join(f"{term}={score:.5f}" for term, score in terms)
        print(f"{doc.doc_id:28}  {pretty}")


def _print_rank(rows: list[tuple[Document, float]]) -> None:
    for doc, score in rows:
        print(f"{score:8.4f}  {doc.doc_id:28}  {doc.title}")


def cmd_demo(_args: argparse.Namespace) -> int:
    print("== commonplace book (original notes) ==")
    notes = load_commonplace()
    index = TfIdfIndex(notes)
    _print_top(index, k=6)
    print()
    print("query: hypo fixer enlarger")
    _print_rank(index.rank("hypo fixer enlarger", k=3))
    print("query: zugzwang lucena opposition")
    _print_rank(index.rank("zugzwang lucena opposition", k=3))
    print()
    print("== Alice chapters ==")
    alice = TfIdfIndex(load_chapters("carroll-alice"))
    _print_top(alice, k=5)
    print()
    print("query: hatter hare tea")
    _print_rank(alice.rank("hatter hare tea", k=3))
    return 0


def cmd_bible(args: argparse.Namespace) -> int:
    books = load_bible()
    index = TfIdfIndex(books)
    print(f"{len(books)} units (expected {len(expected_book_ids())})")
    if args.book:
        if args.book not in {doc.doc_id for doc in books}:
            print(f"unknown book {args.book!r}", file=sys.stderr)
            return 2
        for term, score in index.top_terms(args.book, k=args.k):
            print(f"{score:.6f}\t{term}")
        return 0
    _print_top(index, k=args.k)
    return 0


def cmd_chapters(args: argparse.Namespace) -> int:
    docs = load_chapters(args.stem)
    index = TfIdfIndex(docs)
    print(f"{args.stem}: {len(docs)} units")
    _print_top(index, k=args.k)
    return 0


def cmd_voices(args: argparse.Namespace) -> int:
    docs = load_speakers(args.play)
    index = TfIdfIndex(docs)
    print(f"{args.play}: {len(docs)} voices")
    _print_top(index, k=args.k)
    return 0


def cmd_rank(args: argparse.Namespace) -> int:
    index = _index_for_units(args)
    _print_rank(index.rank(args.query, k=args.k))
    return 0


def cmd_passages(args: argparse.Namespace) -> int:
    path = Path(args.file)
    if not path.is_file():
        path = GUTENBERG / args.file
        if not path.suffix:
            path = GUTENBERG / f"{args.file}.txt"
    text = path.read_text(encoding="utf-8", errors="replace")
    rows = rank_passages(
        text,
        args.query,
        source=str(path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path),
        window=args.window,
        stride=args.stride,
        k=args.k,
    )
    for passage, score in rows:
        snippet = passage.text[:160].replace("\n", " ")
        print(f"{score:8.4f}  {passage.doc_id}  [{passage.start_token}:{passage.end_token}]")
        print(f"          {snippet}")
    return 0


def cmd_commonplace(args: argparse.Namespace) -> int:
    notes = load_commonplace()
    index = TfIdfIndex(notes)
    if args.query:
        _print_rank(index.rank(args.query, k=args.k))
        return 0
    _print_top(index, k=args.k)
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    index = _index_for_units(args)
    rows = index.distinctive_overlap(args.left, args.right, k=args.k)
    print(f"{'term':16}  {args.left:14}  {args.right:14}")
    for term, lv, rv in rows:
        print(f"{term:16}  {lv:14.6f}  {rv:14.6f}")
    return 0


def _index_for_units(args: argparse.Namespace) -> TfIdfIndex:
    units = getattr(args, "units", "commonplace")
    if units == "bible":
        return TfIdfIndex(load_bible())
    if units == "chapters":
        if not args.stem:
            raise SystemExit("--stem is required for --units chapters")
        return TfIdfIndex(load_chapters(args.stem))
    if units == "voices":
        if not args.play:
            raise SystemExit("--play is required for --units voices")
        return TfIdfIndex(load_speakers(args.play))
    if units == "gutenberg":
        docs = []
        for path in sorted(GUTENBERG.glob("*.txt")):
            docs.append(
                Document(
                    doc_id=path.stem,
                    title=path.stem,
                    text=path.read_text(encoding="utf-8", errors="replace"),
                    source=str(path.relative_to(REPO_ROOT)),
                )
            )
        return TfIdfIndex(docs)
    return TfIdfIndex(load_commonplace())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="shelf_units",
        description="Personal TF-IDF study kit: bible books, chapters, voices, notes.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    demo = sub.add_parser("demo", help="short commonplace + Alice walk")
    demo.set_defaults(func=cmd_demo)

    bible = sub.add_parser("bible", help="top terms per King James book")
    bible.add_argument("--book", help="single book id, e.g. genesis")
    bible.add_argument("-k", type=int, default=6)
    bible.set_defaults(func=cmd_bible)

    chapters = sub.add_parser("chapters", help="top terms per chapter/book unit")
    chapters.add_argument("stem", choices=sorted(SPLITTERS))
    chapters.add_argument("-k", type=int, default=6)
    chapters.set_defaults(func=cmd_chapters)

    voices = sub.add_parser("voices", help="top terms per Folio speaker")
    voices.add_argument("play", choices=sorted(ALIASES))
    voices.add_argument("-k", type=int, default=6)
    voices.set_defaults(func=cmd_voices)

    rank = sub.add_parser("rank", help="cosine-rank a query against a unit set")
    rank.add_argument("query")
    rank.add_argument("--units", choices=["commonplace", "bible", "chapters", "voices", "gutenberg"], default="commonplace")
    rank.add_argument("--stem", help="chapterized file stem")
    rank.add_argument("--play", help="speaker-map play stem")
    rank.add_argument("-k", type=int, default=5)
    rank.set_defaults(func=cmd_rank)

    compare = sub.add_parser("compare", help="largest tf-idf gaps between two units")
    compare.add_argument("left")
    compare.add_argument("right")
    compare.add_argument("--units", choices=["commonplace", "bible", "chapters", "voices", "gutenberg"], default="bible")
    compare.add_argument("--stem")
    compare.add_argument("--play")
    compare.add_argument("-k", type=int, default=8)
    compare.set_defaults(func=cmd_compare)

    passages = sub.add_parser("passages", help="sliding-window retrieval in one file")
    passages.add_argument("query")
    passages.add_argument("--file", default="carroll-alice")
    passages.add_argument("--window", type=int, default=80)
    passages.add_argument("--stride", type=int, default=40)
    passages.add_argument("-k", type=int, default=5)
    passages.set_defaults(func=cmd_passages)

    notes = sub.add_parser("commonplace", help="personal notes: tops or a query")
    notes.add_argument("query", nargs="?")
    notes.add_argument("-k", type=int, default=6)
    notes.set_defaults(func=cmd_commonplace)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
