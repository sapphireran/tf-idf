#!/usr/bin/env python3
"""Compute normalized tf, df, idf, and tf-idf for a folder of text files.

Default formulas match the teaching snapshot in this repo:

    tf(t, d)  = count(t, d) / tokens(d)     # empty tokens omitted
    idf(t)    = ln(N / df(t))               # natural log, no smoothing
    tfidf     = tf * idf
    N         = number of documents scored  # not readdir last-index

Writes TSV files in the same layout as output/tf, output/idf, output/tfidf.
See docs/tf-idf-explained.md and examples/hand-calculation.md.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

NON_ALNUM = re.compile(r"[^a-z0-9 ]")

# Tiny teaching stoplist — not a linguistic claim. Used only with --stop so
# you can see the same five documents with and without function words.
STOPWORDS = frozenset(
    {
        "a",
        "an",
        "the",
        "and",
        "or",
        "but",
        "if",
        "to",
        "of",
        "in",
        "on",
        "for",
        "with",
        "as",
        "at",
        "by",
        "from",
        "is",
        "are",
        "was",
        "were",
        "be",
        "this",
        "that",
        "it",
        "its",
        "i",
        "we",
        "you",
        "he",
        "she",
        "they",
        "not",
        "no",
        "do",
        "does",
        "did",
        "then",
        "than",
        "when",
        "after",
        "because",
        "only",
        "so",
        "would",
        "could",
        "should",
        "has",
        "had",
        "have",
        "their",
        "them",
        "his",
        "her",
        "our",
        "my",
    }
)


def tokenize(text: str) -> list[str]:
    """Apply the Perl pipeline cleanup; drop empty fields.

    The original tf-idf-values.pl increments its token counter for empty
    split fields and then skips them when filling %tf. This helper skips
    them in both places so a hand count of visible words matches the
    denominator. On these short documents the two rules agree.
    """
    tokens: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.replace("\r", "")
        line = re.sub(r"\s+", " ", line)
        line = line.lower()
        line = NON_ALNUM.sub("", line)
        for part in line.split(" "):
            if part:
                tokens.append(part)
    return tokens


@dataclass
class Document:
    name: str
    tokens: list[str]
    counts: Counter[str] = field(init=False)

    def __post_init__(self) -> None:
        self.counts = Counter(self.tokens)

    @property
    def n_tokens(self) -> int:
        return len(self.tokens)

    def tf(self, term: str) -> float:
        if self.n_tokens == 0:
            return 0.0
        return self.counts[term] / self.n_tokens


@dataclass
class Collection:
    documents: list[Document]

    @property
    def n_docs(self) -> int:
        return len(self.documents)

    def vocabulary(self) -> list[str]:
        vocab: set[str] = set()
        for doc in self.documents:
            vocab.update(doc.counts)
        return sorted(vocab)

    def df(self, term: str) -> int:
        return sum(1 for doc in self.documents if doc.counts[term])

    def documents_with(self, term: str) -> list[str]:
        return [doc.name for doc in self.documents if doc.counts[term]]

    def idf_raw(self, term: str) -> float:
        df = self.df(term)
        if df == 0:
            raise KeyError(f"term {term!r} is not in the collection")
        return math.log(self.n_docs / df)

    def idf_smooth(self, term: str) -> float:
        return self.idf_raw(term) + 1.0

    def idf_add1(self, term: str) -> float:
        return math.log((self.n_docs + 1) / (self.df(term) + 1)) + 1.0

    def idf_prob(self, term: str) -> float:
        df = self.df(term)
        numer = self.n_docs - df
        if numer <= 0:
            # ln(0) is undefined; a term in every document gets -inf in
            # the unguarded probabilistic form. Report 0 so the table
            # stays printable and matches the "guarded" discussion.
            return 0.0 if df == self.n_docs else math.log(numer / df)
        return math.log(numer / df)

    def tfidf(self, term: str, doc: Document) -> float:
        return doc.tf(term) * self.idf_raw(term)


def load_collection(docs_dir: Path, stop: bool = False) -> Collection:
    paths = sorted(p for p in docs_dir.iterdir() if p.is_file() and p.suffix == ".txt")
    if not paths:
        raise SystemExit(f"no .txt files in {docs_dir}")
    documents = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        tokens = tokenize(text)
        if stop:
            tokens = [tok for tok in tokens if tok not in STOPWORDS]
        documents.append(Document(name=path.name, tokens=tokens))
    return Collection(documents)


def write_tsv(path: Path, rows: list[tuple[str, ...]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write("\t".join(row) + "\n")


def write_outputs(collection: Collection, out_dir: Path) -> None:
    tf_dir = out_dir / "tf"
    tfidf_dir = out_dir / "tfidf"
    tf_dir.mkdir(parents=True, exist_ok=True)
    tfidf_dir.mkdir(parents=True, exist_ok=True)

    df_rows = [("word", "#docs it exists in", "doc names")]
    idf_rows: list[tuple[str, ...]] = []
    for term in collection.vocabulary():
        names = ", ".join(collection.documents_with(term)) + ","
        df_rows.append((term, str(collection.df(term)), names))
        idf_rows.append((term, format(collection.idf_raw(term), ".12g")))

    write_tsv(out_dir / "df.txt", df_rows)
    write_tsv(out_dir / "idf.txt", idf_rows)

    for doc in collection.documents:
        tf_rows = []
        tfidf_rows = []
        for term in sorted(doc.counts):
            tf_rows.append((term, format(doc.tf(term), ".12g")))
            tfidf_rows.append((term, format(collection.tfidf(term, doc), ".12g")))
        write_tsv(tf_dir / doc.name, tf_rows)
        write_tsv(tfidf_dir / doc.name, tfidf_rows)


def ranked_terms(collection: Collection, doc: Document) -> list[tuple[str, float, float, float]]:
    rows = []
    for term in doc.counts:
        rows.append((term, doc.tf(term), collection.idf_raw(term), collection.tfidf(term, doc)))
    rows.sort(key=lambda item: (-item[3], item[0]))
    return rows


def print_rankings(collection: Collection, top_n: int, variants: bool) -> None:
    print(f"N = {collection.n_docs} documents")
    print(f"vocabulary = {len(collection.vocabulary())} terms")
    print()
    for doc in collection.documents:
        print(f"== {doc.name}  ({doc.n_tokens} tokens)")
        header = f"{'term':16} {'tf':>10} {'idf':>12} {'tfidf':>12}"
        if variants:
            header += f" {'idf+1':>12} {'add1':>12} {'prob':>12}"
        print(header)
        for term, tf, idf, tfidf in ranked_terms(collection, doc)[:top_n]:
            line = f"{term:16} {tf:10.6f} {idf:12.6f} {tfidf:12.6f}"
            if variants:
                line += (
                    f" {collection.idf_smooth(term):12.6f}"
                    f" {collection.idf_add1(term):12.6f}"
                    f" {collection.idf_prob(term):12.6f}"
                )
            print(line)
        print()


def print_explain(collection: Collection, term: str, variants: bool) -> None:
    term = term.lower()
    if collection.df(term) == 0:
        raise SystemExit(f"term {term!r} does not appear in this collection")
    print(f"term: {term}")
    print(f"df:   {collection.df(term)} / {collection.n_docs}")
    print(f"docs: {', '.join(collection.documents_with(term))}")
    print(f"idf_raw:    {collection.idf_raw(term):.10f}   ln(N/df)")
    if variants:
        print(f"idf_smooth: {collection.idf_smooth(term):.10f}   ln(N/df)+1")
        print(f"idf_add1:   {collection.idf_add1(term):.10f}   ln((N+1)/(df+1))+1")
        print(f"idf_prob:   {collection.idf_prob(term):.10f}   ln((N-df)/df) or 0 if df=N")
    print()
    print(f"{'document':24} {'count':>6} {'tf':>10} {'tfidf_raw':>12}")
    for doc in collection.documents:
        count = doc.counts[term]
        print(
            f"{doc.name:24} {count:6d} {doc.tf(term):10.6f} "
            f"{collection.tfidf(term, doc):12.6f}"
        )


def build_parser() -> argparse.ArgumentParser:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--docs",
        type=Path,
        default=here / "documents",
        help="folder of .txt documents (default: examples/tiny-corpus/documents)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=here / "output",
        help="output folder (default: examples/tiny-corpus/output)",
    )
    parser.add_argument(
        "--n",
        type=int,
        default=12,
        help="how many top terms to print per document",
    )
    parser.add_argument(
        "--explain",
        metavar="TERM",
        help="print df/idf/tf for one term and skip the ranking table",
    )
    parser.add_argument(
        "--variants",
        action="store_true",
        help="also print smoothed / add-one / probabilistic idf",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="print only; do not write TSV files",
    )
    parser.add_argument(
        "--stop",
        action="store_true",
        help="drop a small English stoplist before scoring (teaching contrast)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    collection = load_collection(args.docs, stop=args.stop)
    if not args.no_write:
        write_outputs(collection, args.out)
        print(f"wrote tf / df / idf / tfidf under {args.out}", file=sys.stderr)
    if args.explain:
        print_explain(collection, args.explain, args.variants)
    else:
        print_rankings(collection, args.n, args.variants)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
