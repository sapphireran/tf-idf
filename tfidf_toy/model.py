"""In-memory tf-idf index plus the legacy TSV layout under output/."""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator

from .tokenize import load_corpus, tokenize

RAW = "raw"
SMOOTH = "smooth"
IDF_MODES = (RAW, SMOOTH)


def format_score(value: float) -> str:
    """Stable enough for TSV dumps and CLI tables."""
    return format(value, ".15g")


def idf_value(n_docs: int, df: int, mode: str = RAW) -> float:
    if df <= 0:
        raise ValueError("df must be positive")
    if n_docs <= 0:
        raise ValueError("n_docs must be positive")
    if mode == RAW:
        return math.log(n_docs / df)
    if mode == SMOOTH:
        return math.log((n_docs + 1) / (df + 1)) + 1.0
    raise ValueError(f"unknown idf mode {mode!r}; expected {IDF_MODES}")


@dataclass
class DocumentModel:
    name: str
    tokens: list[str]
    length: int
    counts: Counter[str]
    tf: dict[str, float]
    tfidf: dict[str, float] = field(default_factory=dict)

    def top_terms(self, k: int = 15) -> list[tuple[str, float]]:
        ranked = sorted(self.tfidf.items(), key=lambda kv: (-kv[1], kv[0]))
        if k < 0:
            return ranked
        return ranked[:k]

    def score(self, term: str) -> float:
        return self.tfidf.get(term, 0.0)


@dataclass
class TfIdfIndex:
    documents: dict[str, DocumentModel]
    df: dict[str, int]
    idf: dict[str, float]
    n_docs: int
    idf_mode: str
    postings: dict[str, set[str]]
    match_perl_length: bool = False

    def __iter__(self) -> Iterator[DocumentModel]:
        for name in sorted(self.documents):
            yield self.documents[name]

    def get(self, name: str) -> DocumentModel:
        try:
            return self.documents[name]
        except KeyError as exc:
            known = ", ".join(sorted(self.documents))
            raise KeyError(f"unknown document {name!r}; have: {known}") from exc

    @classmethod
    def from_texts(
        cls,
        texts: dict[str, str],
        *,
        idf_mode: str = RAW,
        match_perl_length: bool = False,
    ) -> "TfIdfIndex":
        if not texts:
            raise ValueError("need at least one document")
        if idf_mode not in IDF_MODES:
            raise ValueError(f"unknown idf mode {idf_mode!r}")

        documents: dict[str, DocumentModel] = {}
        postings: dict[str, set[str]] = defaultdict(set)

        for name, text in texts.items():
            tokens, length = tokenize(text, match_perl_length=match_perl_length)
            counts: Counter[str] = Counter(tokens)
            if length == 0:
                tf: dict[str, float] = {}
            else:
                tf = {term: count / length for term, count in counts.items()}
            documents[name] = DocumentModel(
                name=name,
                tokens=tokens,
                length=length,
                counts=counts,
                tf=tf,
            )
            for term in counts:
                postings[term].add(name)

        n_docs = len(documents)
        df = {term: len(names) for term, names in postings.items()}
        idf = {term: idf_value(n_docs, df_t, idf_mode) for term, df_t in df.items()}

        for doc in documents.values():
            doc.tfidf = {term: tf_t * idf[term] for term, tf_t in doc.tf.items()}

        return cls(
            documents=documents,
            df=df,
            idf=idf,
            n_docs=n_docs,
            idf_mode=idf_mode,
            postings=dict(postings),
            match_perl_length=match_perl_length,
        )

    @classmethod
    def from_directory(
        cls,
        directory: Path,
        *,
        idf_mode: str = RAW,
        match_perl_length: bool = False,
    ) -> "TfIdfIndex":
        return cls.from_texts(
            load_corpus(Path(directory)),
            idf_mode=idf_mode,
            match_perl_length=match_perl_length,
        )

    def compare(
        self, left_name: str, right_name: str, *, k: int = 12
    ) -> tuple[list[tuple[str, float, float, float]], list[tuple[str, float, float, float]]]:
        """Return terms with the largest tf-idf gaps left-vs-right and right-vs-left.

        Each tuple is ``(term, score_left, score_right, delta)`` where
        ``delta = score_left - score_right`` for the first list and the
        opposite sign for the second.
        """
        left = self.get(left_name)
        right = self.get(right_name)
        vocab = set(left.tfidf) | set(right.tfidf)
        scored: list[tuple[str, float, float, float]] = []
        for term in vocab:
            s_left = left.score(term)
            s_right = right.score(term)
            scored.append((term, s_left, s_right, s_left - s_right))
        distinctive_left = sorted(scored, key=lambda row: (-row[3], row[0]))[:k]
        distinctive_right = sorted(
            ((term, s_l, s_r, s_r - s_l) for term, s_l, s_r, _ in scored),
            key=lambda row: (-row[3], row[0]),
        )[:k]
        return distinctive_left, distinctive_right

    def write_legacy_output(self, outdir: Path) -> None:
        """Write tf/, idf.txt, df.txt, and tfidf/ in the original Perl layout."""
        outdir = Path(outdir)
        tf_dir = outdir / "tf"
        tfidf_dir = outdir / "tfidf"
        tf_dir.mkdir(parents=True, exist_ok=True)
        tfidf_dir.mkdir(parents=True, exist_ok=True)

        for doc in self.documents.values():
            _write_term_table(tf_dir / doc.name, doc.tf)
            _write_term_table(tfidf_dir / doc.name, doc.tfidf)

        with (outdir / "idf.txt").open("w", encoding="utf-8") as handle:
            for term in sorted(self.idf):
                handle.write(f"{term}\t{format_score(self.idf[term])}\n")

        with (outdir / "df.txt").open("w", encoding="utf-8") as handle:
            handle.write("word \t #docs it exists in \t doc names\n")
            for term in sorted(self.postings):
                names = ", ".join(sorted(self.postings[term]))
                handle.write(f"{term}\t{len(self.postings[term])}\t{names}, \n")


def _write_term_table(path: Path, values: dict[str, float]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for term in sorted(values):
            handle.write(f"{term}\t{format_score(values[term])}\n")


_LEADING_FLOAT = re.compile(r"^[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?")


def load_term_table(path: Path) -> dict[str, float]:
    """Load a ``term<TAB>float`` file such as output/tfidf/carroll-alice.txt.

    The committed ``output/idf.txt`` has one smashed row
    (``thatyou\\t2.89037175789616y``) from the original Perl dump. A trailing
    non-numeric fragment is ignored so the rest of the table still loads.
    """
    table: dict[str, float] = {}
    for line_no, line in enumerate(
        Path(path).read_text(encoding="utf-8", errors="replace").splitlines(), start=1
    ):
        stripped = line.strip()
        if not stripped or stripped.startswith("word \t"):
            continue
        if "\t" not in stripped:
            raise ValueError(f"{path}:{line_no}: missing tab in {line!r}")
        term, raw_score = stripped.split("\t", 1)
        raw_score = raw_score.strip()
        try:
            table[term] = float(raw_score)
            continue
        except ValueError:
            match = _LEADING_FLOAT.match(raw_score)
            if not match:
                raise ValueError(f"{path}:{line_no}: bad score in {line!r}") from None
            table[term] = float(match.group(0))
    return table


def iter_tfidf_dir(directory: Path) -> Iterable[tuple[str, dict[str, float]]]:
    directory = Path(directory)
    for path in sorted(directory.iterdir()):
        if path.name.startswith(".") or not path.is_file():
            continue
        yield path.name, load_term_table(path)


def rank_overlap(
    left: dict[str, float], right: dict[str, float], *, k: int = 50
) -> tuple[int, list[str], list[str]]:
    """How many of the top-k terms (by score) are shared?"""

    def top_names(table: dict[str, float]) -> list[str]:
        ranked = sorted(table.items(), key=lambda kv: (-kv[1], kv[0]))
        return [term for term, _ in ranked[:k]]

    left_names = top_names(left)
    right_names = top_names(right)
    overlap = len(set(left_names) & set(right_names))
    return overlap, left_names, right_names
