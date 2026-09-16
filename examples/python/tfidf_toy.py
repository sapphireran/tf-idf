#!/usr/bin/env python3
"""Educational tf-idf that mirrors the 2012 Perl Gutenberg toy.

Intended formula (what the committed output/ tables used):

    tf(t, d)    = count(t, d) / |d|
    idf(t)      = ln(N / df(t))
    tfidf(t, d) = tf(t, d) * idf(t)

N is the number of documents actually tokenized, not Perl's ``$#files``.
See docs/formula-and-implementation-notes.md for the differences.

This file is both a small library (``score_corpus``) and a CLI:

    python3 examples/python/tfidf_toy.py examples/tiny-corpus/documents \\
        --write-dir examples/tiny-corpus/output
    python3 examples/python/tfidf_toy.py gutenberg --write-dir /tmp/gutenberg-tfidf
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Mapping

# Names the 2012 checkout left lying around. Never treat them as books.
_SKIP_NAMES = {".DS_Store", "Thumbs.db"}

# After chomp, collapse every remaining whitespace run the way
# $txt =~ s/[\h\v]+/ /g plus later split(/ +/) do for ASCII Gutenberg text.
_WHITESPACE_RUN = re.compile(r"\s+")
_KEEP_TOKEN_CHARS = re.compile(r"[^a-zA-Z0-9\s]")


def tokenize_line(line: str) -> list[str]:
    """Apply the four Perl cleanup steps to one raw line, then split on spaces.

    Empty strings from a leading/trailing space are kept in the returned list
    so callers can decide whether they inflate ``|d|`` (Perl does).
    """
    text = line.rstrip("\n\r")
    text = _WHITESPACE_RUN.sub(" ", text)
    text = text.lower()
    text = _KEEP_TOKEN_CHARS.sub("", text)
    if text == "":
        return [""]
    return text.split(" ")


def tokenize_text(text: str, count_empties: bool = False) -> list[str]:
    """Tokenize a whole document (newline-separated lines)."""
    tokens: list[str] = []
    for line in text.splitlines():
        for token in tokenize_line(line):
            if token == "":
                if count_empties:
                    tokens.append(token)
            else:
                tokens.append(token)
    return tokens


def iter_corpus_files(corpus_dir: Path) -> Iterator[Path]:
    """Yield document files in sorted order, skipping dotfiles and junk names."""
    if not corpus_dir.is_dir():
        raise FileNotFoundError(f"corpus directory not found: {corpus_dir}")
    for path in sorted(corpus_dir.iterdir()):
        if not path.is_file():
            continue
        if path.name.startswith("."):
            continue
        if path.name in _SKIP_NAMES:
            continue
        yield path


@dataclass(frozen=True)
class DocumentScores:
    name: str
    tokens: list[str]
    tf: dict[str, float]
    tfidf: dict[str, float]

    @property
    def length(self) -> int:
        return len(self.tokens)


@dataclass(frozen=True)
class CorpusScores:
    documents: list[DocumentScores]
    df: dict[str, int]
    idf: dict[str, float]
    n_documents: int
    document_names: dict[str, list[str]]

    def by_name(self) -> dict[str, DocumentScores]:
        return {doc.name: doc for doc in self.documents}


def score_tokens(
    named_token_lists: Mapping[str, list[str]],
) -> CorpusScores:
    """Compute tf / df / idf / tf*idf for an in-memory corpus.

    ``named_token_lists`` maps a document id (usually a filename) to the
    tokens that count toward |d|. Empty-string tokens should already have
    been dropped unless you are reproducing the Perl denominator.
    """
    names = list(named_token_lists)
    n = len(names)
    if n == 0:
        raise ValueError("corpus is empty")

    df: dict[str, int] = Counter()
    docs_for_term: dict[str, list[str]] = defaultdict(list)
    raw_counts: dict[str, Counter[str]] = {}

    for name in names:
        tokens = named_token_lists[name]
        counts = Counter(token for token in tokens if token != "")
        raw_counts[name] = counts
        for token in counts:
            df[token] += 1
            docs_for_term[token].append(name)

    idf = {token: math.log(n / df_t) for token, df_t in df.items()}

    documents: list[DocumentScores] = []
    for name in names:
        tokens = named_token_lists[name]
        length = len(tokens)
        if length == 0:
            raise ValueError(f"document {name!r} has no tokens")
        tf = {token: count / length for token, count in raw_counts[name].items()}
        tfidf = {token: tf[token] * idf[token] for token in tf}
        documents.append(DocumentScores(name=name, tokens=list(tokens), tf=tf, tfidf=tfidf))

    return CorpusScores(
        documents=documents,
        df=dict(df),
        idf=idf,
        n_documents=n,
        document_names={token: list(names_for) for token, names_for in docs_for_term.items()},
    )


def score_corpus(corpus_dir: Path, count_empties: bool = False) -> CorpusScores:
    """Read every non-dot file in ``corpus_dir`` and score the collection."""
    named: dict[str, list[str]] = {}
    for path in iter_corpus_files(corpus_dir):
        text = path.read_text(encoding="utf-8", errors="replace")
        named[path.name] = tokenize_text(text, count_empties=count_empties)
    if not named:
        raise ValueError(f"no documents found in {corpus_dir}")
    return score_tokens(named)


def _format_float(value: float) -> str:
    """Plain, parseable float (avoid scientific notation for tiny weights)."""
    if value == 0:
        return "0"
    return f"{value:.15g}"


def write_tables(scores: CorpusScores, write_dir: Path) -> None:
    """Write Perl-shaped tf / df / idf / tfidf text tables."""
    tf_dir = write_dir / "tf"
    tfidf_dir = write_dir / "tfidf"
    tf_dir.mkdir(parents=True, exist_ok=True)
    tfidf_dir.mkdir(parents=True, exist_ok=True)

    for doc in scores.documents:
        tf_lines = [f"{token}\t{_format_float(doc.tf[token])}\n" for token in sorted(doc.tf)]
        tfidf_lines = [f"{token}\t{_format_float(doc.tfidf[token])}\n" for token in sorted(doc.tfidf)]
        (tf_dir / doc.name).write_text("".join(tf_lines), encoding="utf-8")
        (tfidf_dir / doc.name).write_text("".join(tfidf_lines), encoding="utf-8")

    df_rows = ["word\t#docs it exists in\tdoc names\n"]
    idf_rows: list[str] = []
    for token in sorted(scores.df):
        names = ", ".join(scores.document_names[token])
        df_rows.append(f"{token}\t{scores.df[token]}\t{names},\n")
        idf_rows.append(f"{token}\t{_format_float(scores.idf[token])}\n")

    (write_dir / "df.txt").write_text("".join(df_rows), encoding="utf-8")
    (write_dir / "idf.txt").write_text("".join(idf_rows), encoding="utf-8")


def load_weight_table(path: Path) -> dict[str, float]:
    """Load a two-column token<TAB>float file (tf, idf, or tfidf).

    Rows whose second column is not a float are skipped (the committed
    ``output/idf.txt`` has one corrupt ``thatyou`` line).
    """
    weights: dict[str, float] = {}
    text = path.read_text(encoding="utf-8", errors="replace")
    for lineno, raw in enumerate(text.splitlines(), start=1):
        if not raw or raw.startswith("word\t"):
            continue
        parts = raw.split("\t")
        if len(parts) < 2:
            continue
        token, value = parts[0], parts[1]
        try:
            weights[token] = float(value)
        except ValueError:
            print(
                f"warning: {path}:{lineno} skipping non-float weight {value!r}",
                file=sys.stderr,
            )
    return weights


def ranked_terms(weights: Mapping[str, float], top: int | None = None) -> list[tuple[str, float]]:
    """Return (token, weight) pairs, highest weight first, ties alphabetical."""
    items = sorted(weights.items(), key=lambda item: (-item[1], item[0]))
    if top is not None:
        return items[:top]
    return items


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute tf, idf, and tf*idf for a directory of text files."
    )
    parser.add_argument(
        "corpus",
        type=Path,
        help="directory of documents (gutenberg/ or examples/tiny-corpus/documents)",
    )
    parser.add_argument(
        "--write-dir",
        type=Path,
        help="write tf/, df.txt, idf.txt, tfidf/ here",
    )
    parser.add_argument(
        "--count-empties",
        action="store_true",
        help="count empty split leftovers in |d|, like tf-idf-values.pl",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=8,
        help="print this many top terms per document (0 to skip)",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    scores = score_corpus(args.corpus, count_empties=args.count_empties)
    print(f"N={scores.n_documents} documents from {args.corpus}")
    print(f"vocabulary={len(scores.idf)} distinct tokens")

    if args.top:
        for doc in scores.documents:
            print(f"\n# {doc.name}  (|d|={doc.length})")
            for token, weight in ranked_terms(doc.tfidf, top=args.top):
                print(f"  {token:20s} {weight:.8g}")

    if args.write_dir:
        write_tables(scores, args.write_dir)
        print(f"\nwrote tables under {args.write_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
