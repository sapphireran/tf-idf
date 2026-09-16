#!/usr/bin/env python3
"""Educational tf-idf matching this repo's 2012 Perl walkthrough.

Default formula
---------------
    tf(t, d)    = count(t, d) / tokens(d)
    idf(t)      = ln(N / df(t))
    tfidf(t, d) = tf(t, d) * idf(t)

N is the number of files actually tokenized, not Perl's ``$#files``.
Tokenization follows the historical script: lowercase, strip characters
that are not alphanumeric or whitespace, split on spaces.

This module is stdlib-only so it runs in a bare personal checkout.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

HIDDEN_NAME = re.compile(r"^\.")
WHITESPACE = re.compile(r"[ \t\n\r\f\v]+")
KEEP_TOKEN_CHARS = re.compile(r"[^a-z0-9\s]")


def tokenize(text: str, *, faithful_perl: bool = False) -> List[str]:
    """Normalize one document the way ``tf-idf-values.pl`` does.

    If ``faithful_perl`` is true, leading empty fields from a split on
    spaces are kept in the returned list (they inflate the historical
    ``$word_count`` denominator). The default drops empty tokens.
    """
    collapsed = WHITESPACE.sub(" ", text)
    lowered = collapsed.lower()
    stripped = KEEP_TOKEN_CHARS.sub("", lowered)
    parts = stripped.split(" ")
    if faithful_perl:
        # Perl split(/ +/, ...) keeps a leading empty field and drops
        # trailing empties. Reproduce that, including a leading "" when
        # the line starts with a space.
        if parts and parts[-1] == "":
            parts = parts[:-1]
        return parts
    return [part for part in parts if part]


@dataclass
class Document:
    name: str
    tokens: List[str]
    counts: Dict[str, int] = field(init=False)
    length: int = field(init=False)

    def __post_init__(self) -> None:
        self.counts = {}
        length = 0
        for token in self.tokens:
            length += 1
            if token == "":
                continue
            self.counts[token] = self.counts.get(token, 0) + 1
        self.length = length

    def tf(self, term: str) -> float:
        if self.length == 0:
            return 0.0
        return self.counts.get(term, 0) / self.length


@dataclass
class TfidfIndex:
    documents: List[Document]
    df: Dict[str, int]
    idf: Dict[str, float]
    idf_variant: str
    N: int

    def tfidf(self, document: Document) -> Dict[str, float]:
        return {
            term: document.tf(term) * self.idf[term]
            for term in document.counts
        }

    def ranked(self, document: Document, limit: Optional[int] = None) -> List[Tuple[str, float]]:
        rows = sorted(
            self.tfidf(document).items(),
            key=lambda item: (-item[1], item[0]),
        )
        if limit is not None:
            return rows[:limit]
        return rows

    def vector(self, document: Document) -> Dict[str, float]:
        return self.tfidf(document)

    def document_by_name(self, name: str) -> Document:
        for document in self.documents:
            if document.name == name:
                return document
        raise KeyError(f"no document named {name!r}")


def compute_idf(df: Mapping[str, int], n_docs: int, variant: str) -> Dict[str, float]:
    if n_docs <= 0:
        raise ValueError("N must be at least 1")
    values = {}
    for term, document_freq in df.items():
        if document_freq <= 0:
            continue
        if variant == "raw":
            values[term] = math.log(n_docs / document_freq)
        elif variant == "smooth":
            values[term] = math.log(n_docs / (1.0 + document_freq)) + 1.0
        elif variant == "sklearn":
            values[term] = math.log((n_docs + 1.0) / (document_freq + 1.0)) + 1.0
        else:
            raise ValueError(f"unknown idf variant {variant!r}")
    return values


def build_index(
    documents: Sequence[Document],
    *,
    idf_variant: str = "raw",
) -> TfidfIndex:
    df: Dict[str, int] = {}
    for document in documents:
        for term in document.counts:
            df[term] = df.get(term, 0) + 1
    n_docs = len(documents)
    return TfidfIndex(
        documents=list(documents),
        df=df,
        idf=compute_idf(df, n_docs, idf_variant),
        idf_variant=idf_variant,
        N=n_docs,
    )


def load_directory(
    path: Path,
    *,
    faithful_perl: bool = False,
    suffix: str = ".txt",
) -> List[Document]:
    if not path.is_dir():
        raise FileNotFoundError(f"corpus directory not found: {path}")
    documents = []
    for entry in sorted(path.iterdir()):
        if not entry.is_file():
            continue
        if HIDDEN_NAME.match(entry.name):
            continue
        if suffix and not entry.name.endswith(suffix):
            continue
        text = entry.read_text(encoding="utf-8", errors="replace")
        documents.append(
            Document(name=entry.name, tokens=tokenize(text, faithful_perl=faithful_perl))
        )
    if not documents:
        raise ValueError(f"no documents found in {path}")
    return documents


def cosine_similarity(left: Mapping[str, float], right: Mapping[str, float]) -> float:
    if not left or not right:
        return 0.0
    dot = 0.0
    for term, value in left.items():
        other = right.get(term)
        if other:
            dot += value * other
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return dot / (left_norm * right_norm)


def write_tables(index: TfidfIndex, output_dir: Path) -> None:
    """Write tf / df / idf / tfidf tables in the same tab layout as output/."""
    tf_dir = output_dir / "tf"
    tfidf_dir = output_dir / "tfidf"
    tf_dir.mkdir(parents=True, exist_ok=True)
    tfidf_dir.mkdir(parents=True, exist_ok=True)

    df_path = output_dir / "df.txt"
    idf_path = output_dir / "idf.txt"
    with df_path.open("w", encoding="utf-8") as df_file, idf_path.open(
        "w", encoding="utf-8"
    ) as idf_file:
        df_file.write("word\t#docs it exists in\tdoc names\n")
        postings: Dict[str, List[str]] = {term: [] for term in index.df}
        for document in index.documents:
            for term in document.counts:
                postings[term].append(document.name)
        for term in sorted(index.df):
            names = ", ".join(postings[term])
            df_file.write(f"{term}\t{index.df[term]}\t{names}\n")
            idf_file.write(f"{term}\t{index.idf[term]}\n")

    for document in index.documents:
        tf_rows = [(term, document.tf(term)) for term in sorted(document.counts)]
        tfidf_rows = [(term, score) for term, score in sorted(index.tfidf(document).items())]
        (tf_dir / document.name).write_text(
            "".join(f"{term}\t{value}\n" for term, value in tf_rows),
            encoding="utf-8",
        )
        (tfidf_dir / document.name).write_text(
            "".join(f"{term}\t{value}\n" for term, value in tfidf_rows),
            encoding="utf-8",
        )


def format_ranking(name: str, rows: Sequence[Tuple[str, float]]) -> str:
    lines = [f"## {name}", ""]
    lines.append("| rank | term | tf-idf |")
    lines.append("| ---: | --- | ---: |")
    for rank, (term, score) in enumerate(rows, start=1):
        lines.append(f"| {rank} | {term} | {score:.12g} |")
    lines.append("")
    return "\n".join(lines)


def _print_rankings(index: TfidfIndex, top: int) -> None:
    print(f"N={index.N}  idf={index.idf_variant}  documents={len(index.documents)}")
    print()
    for document in index.documents:
        print(format_ranking(document.name, index.ranked(document, limit=top)))


def _print_similarities(index: TfidfIndex, name: str) -> None:
    target = index.document_by_name(name)
    target_vec = index.vector(target)
    print(f"cosine similarity vs {name}  (idf={index.idf_variant})")
    print()
    scored = []
    for document in index.documents:
        scored.append((cosine_similarity(target_vec, index.vector(document)), document.name))
    scored.sort(reverse=True)
    for score, other in scored:
        print(f"{score:.6f}\t{other}")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compute length-normalized tf * ln(N/df) for a directory of texts."
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Directory of .txt documents (hidden files skipped).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional directory for tf/, df.txt, idf.txt, and tfidf/ tables.",
    )
    parser.add_argument("--top", type=int, default=10, help="How many terms to print per file.")
    parser.add_argument(
        "--idf",
        choices=("raw", "smooth", "sklearn"),
        default="raw",
        help="raw is the 2012 formula. sklearn is ln((N+1)/(df+1))+1 without L2.",
    )
    parser.add_argument(
        "--faithful-perl",
        action="store_true",
        help="Count leading empty split fields in the tf denominator.",
    )
    parser.add_argument(
        "--similar",
        metavar="FILE",
        help="Print cosine similarity from FILE to every document and exit.",
    )
    parser.add_argument(
        "--dump-json",
        type=Path,
        help="Write {N, idf, tfidf} JSON (same shape as tiny-corpus/expected.json).",
    )
    return parser


def index_as_expected_payload(index: TfidfIndex) -> dict:
    return {
        "N": index.N,
        "idf": {term: index.idf[term] for term in sorted(index.idf)},
        "tfidf": {
            document.name: {
                term: score for term, score in sorted(index.tfidf(document).items())
            }
            for document in index.documents
        },
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    documents = load_directory(args.input, faithful_perl=args.faithful_perl)
    index = build_index(documents, idf_variant=args.idf)
    if args.output:
        write_tables(index, args.output)
        print(f"wrote tables under {args.output}", file=sys.stderr)
    if args.dump_json:
        args.dump_json.write_text(
            json.dumps(index_as_expected_payload(index), indent=2) + "\n",
            encoding="utf-8",
        )
    if args.similar:
        _print_similarities(index, args.similar)
        return 0
    _print_rankings(index, args.top)
    return 0


if __name__ == "__main__":
    sys.exit(main())
