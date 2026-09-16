"""Teaching TF-IDF library for the personal Gutenberg toy repo.

Formula (matches the checked-in snapshot when N is the file count):

    tf(t, d)     = count(t, d) / words(d)
    idf(t)       = ln(N / df(t))
    tfidf(t, d)  = tf(t, d) * idf(t)

The original Perl scripts are the historical blog-post path. This
module exists so the micro and tiny examples can be recomputed with
tests, and so the same tokenizer can be inspected in one place.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
import math
from pathlib import Path
import re
from typing import Iterable, Mapping

# Collapse the same classes Perl's [\h\v] aims at: horizontal and
# vertical ASCII whitespace. After this pass a line only has spaces.
_WHITESPACE = re.compile(r"[\t\n\v\f\r ]+")
# Run after lowercasing. Digits stay; punctuation does not.
_KEEP = re.compile(r"[^a-z0-9 ]+")


def tokenize_line(line: str, *, keep_empty: bool = False) -> list[str]:
    """Tokenize one line the way tf-idf-values.pl does.

    Order: strip endlines, collapse whitespace, lowercase, drop
    non-alphanumeric characters, split on spaces.

    ``keep_empty=True`` preserves the empty fields Perl still counts
    toward ``$word_count``. The default drops them so TF denominators
    are "number of real tokens."
    """
    line = line.rstrip("\n\r")
    line = _WHITESPACE.sub(" ", line)
    line = line.lower()
    line = _KEEP.sub("", line)
    parts = line.split(" ")
    if keep_empty:
        return parts
    return [part for part in parts if part]


def tokenize_text(text: str, *, keep_empty: bool = False) -> list[str]:
    """Tokenize a whole string, line by line, like the Perl reader."""
    tokens: list[str] = []
    for line in text.splitlines():
        tokens.extend(tokenize_line(line, keep_empty=keep_empty))
    return tokens


def tokenize_path(path: Path, *, keep_empty: bool = False) -> list[str]:
    """Read a text file and tokenize it."""
    data = path.read_text(encoding="utf-8")
    return tokenize_text(data, keep_empty=keep_empty)


def count_tokens(tokens: Iterable[str], *, count_empty: bool = False) -> tuple[Counter[str], int]:
    """Return (term -> raw count, words_d).

    Empty strings are never stored as terms. They increase ``words_d``
    only when ``count_empty`` is true (Perl compatibility).
    """
    counts: Counter[str] = Counter()
    words = 0
    for token in tokens:
        if token == "":
            if count_empty:
                words += 1
            continue
        counts[token] += 1
        words += 1
    return counts, words


def normalized_tf(counts: Mapping[str, int], words: int) -> dict[str, float]:
    """``count / words``. ``words`` must be positive."""
    if words <= 0:
        raise ValueError("document length must be positive")
    return {term: count / words for term, count in counts.items()}


def inverse_document_frequency(n_docs: int, df: int) -> float:
    """``ln(N / df)``. ``df`` must be in ``1..N``."""
    if n_docs <= 0:
        raise ValueError("collection size N must be positive")
    if df <= 0:
        raise ValueError("df must be positive for terms that occurred")
    if df > n_docs:
        raise ValueError("df cannot exceed N")
    return math.log(n_docs / df)


def reconstruct_df(n_docs: int, idf: float) -> float:
    """Invert ``idf = ln(N / df)`` → ``df = N / exp(idf)``."""
    return n_docs / math.exp(idf)


@dataclass
class DocumentScores:
    name: str
    raw_counts: Counter[str]
    words: int
    tf: dict[str, float] = field(default_factory=dict)
    tfidf: dict[str, float] = field(default_factory=dict)


@dataclass
class CollectionScores:
    documents: list[DocumentScores]
    df: dict[str, int]
    idf: dict[str, float]
    postings: dict[str, list[str]]

    @property
    def n_docs(self) -> int:
        return len(self.documents)


def iter_input_files(input_dir: Path) -> list[Path]:
    """Non-hidden ``*.txt`` files, sorted by name.

    READMEs and other notes in an example directory are not documents.
    The original Perl skips only names starting with ``.`` and assumes
    everything else in ``gutenberg/`` is a text file.
    """
    files = [
        path
        for path in input_dir.iterdir()
        if path.is_file()
        and not path.name.startswith(".")
        and path.suffix.lower() == ".txt"
    ]
    return sorted(files, key=lambda path: path.name)


def score_collection(input_dir: Path, *, count_empty: bool = False) -> CollectionScores:
    """Run the two-pass TF-IDF pipeline over every non-hidden file."""
    files = iter_input_files(input_dir)
    if not files:
        raise ValueError(f"no input files in {input_dir}")

    documents: list[DocumentScores] = []
    postings: dict[str, set[str]] = defaultdict(set)

    for path in files:
        tokens = tokenize_path(path, keep_empty=count_empty)
        counts, words = count_tokens(tokens, count_empty=count_empty)
        if words <= 0:
            raise ValueError(f"{path} produced no tokens")
        tf = normalized_tf(counts, words)
        documents.append(
            DocumentScores(name=path.name, raw_counts=counts, words=words, tf=tf)
        )
        for term in counts:
            postings[term].add(path.name)

    n_docs = len(documents)
    df = {term: len(names) for term, names in postings.items()}
    idf = {term: inverse_document_frequency(n_docs, df[term]) for term in df}

    for document in documents:
        document.tfidf = {
            term: document.tf[term] * idf[term] for term in document.tf
        }

    posting_lists = {term: sorted(names) for term, names in postings.items()}
    return CollectionScores(
        documents=documents, df=df, idf=idf, postings=posting_lists
    )


def format_float(value: float) -> str:
    """Stable enough for tests; not a Perl stringification clone."""
    if value == 0:
        return "0"
    return repr(value)


def write_tsv(path: Path, rows: Iterable[tuple[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for key, value in rows:
            handle.write(f"{key}\t{value}\n")


def write_collection(scores: CollectionScores, output_dir: Path) -> None:
    """Write tf/, idf.txt, df.txt, and tfidf/ in the repo's TSV shape."""
    output_dir.mkdir(parents=True, exist_ok=True)
    tf_dir = output_dir / "tf"
    tfidf_dir = output_dir / "tfidf"
    tf_dir.mkdir(exist_ok=True)
    tfidf_dir.mkdir(exist_ok=True)

    for document in scores.documents:
        write_tsv(
            tf_dir / document.name,
            ((term, format_float(document.tf[term])) for term in sorted(document.tf)),
        )
        write_tsv(
            tfidf_dir / document.name,
            (
                (term, format_float(document.tfidf[term]))
                for term in sorted(document.tfidf)
            ),
        )

    write_tsv(
        output_dir / "idf.txt",
        ((term, format_float(scores.idf[term])) for term in sorted(scores.idf)),
    )

    df_path = output_dir / "df.txt"
    with df_path.open("w", encoding="utf-8") as handle:
        handle.write("word \t #docs it exists in \t doc names\n")
        for term in sorted(scores.df):
            names = ", ".join(scores.postings[term]) + ", "
            handle.write(f"{term}\t{scores.df[term]}\t{names}\n")


def top_terms(scores: Mapping[str, float], limit: int) -> list[tuple[str, float]]:
    """Highest score first; ties broken by term name."""
    ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    if limit < 0:
        raise ValueError("limit must be >= 0")
    return ranked[:limit]


def read_score_tsv(path: Path, *, skip_bad: bool = True) -> dict[str, float]:
    """Read a two-column term/score TSV (tf, idf, or tfidf).

    The checked-in ``output/idf.txt`` has one corrupted value
    (``2.89037175789616y`` on ``thatyou``). ``skip_bad=True`` drops
    lines that are not a finite float so snapshot ranking still works.
    """
    scores: dict[str, float] = {}
    with path.open(encoding="utf-8") as handle:
        for raw in handle:
            line = raw.rstrip("\n")
            if not line:
                continue
            if "\t" not in line:
                if skip_bad:
                    continue
                raise ValueError(f"not a two-column TSV line: {line!r}")
            term, value = line.split("\t", 1)
            try:
                scores[term] = float(value)
            except ValueError:
                if skip_bad:
                    continue
                raise
    return scores
