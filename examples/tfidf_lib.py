"""Reference TF-IDF helpers for the personal examples.

The defaults match the 2012 Perl scripts:

* tokenize by lowercasing and deleting non-alphanumeric characters
* TF = raw count / document token length
* IDF = ln(N / df)
* N = number of documents actually read (not readdir length)

Variant flags are opt-in and documented in docs/quirks-and-variants.md.
This module is intentionally stdlib-only.
"""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

IDFMode = str  # "raw" | "smooth" | "prob"
TFMode = str  # "proportion" | "log"


_NON_ALNUM = re.compile(r"[^a-z0-9\s]")
_WS = re.compile(r"\s+")


def tokenize(text: str) -> List[str]:
    """Approximate the Perl tokenizer on a whole document.

    The original script works line-by-line (chomp, collapse \\h/\\v, lower,
    strip punctuation, split on spaces). Processing the whole text after
    translating every whitespace run to a single space is equivalent for
    the ASCII Gutenberg and mini-corpus files.
    """
    lowered = text.lower()
    cleaned = _NON_ALNUM.sub("", lowered)
    collapsed = _WS.sub(" ", cleaned).strip()
    if not collapsed:
        return []
    return collapsed.split(" ")


def read_documents(directory: Path) -> Dict[str, str]:
    """Read ``*.txt`` files in *directory*, ignoring hidden names."""
    docs: Dict[str, str] = {}
    for path in sorted(directory.iterdir()):
        if path.name.startswith("."):
            continue
        if path.suffix.lower() != ".txt":
            continue
        if not path.is_file():
            continue
        docs[path.name] = path.read_text(encoding="utf-8")
    if not docs:
        raise FileNotFoundError(f"no .txt documents in {directory}")
    return docs


@dataclass(frozen=True)
class TfidfModel:
    documents: Mapping[str, Sequence[str]]
    tf: Mapping[str, Mapping[str, float]]
    df: Mapping[str, int]
    idf: Mapping[str, float]
    tfidf: Mapping[str, Mapping[str, float]]
    n_docs: int
    tf_mode: TFMode
    idf_mode: IDFMode

    @property
    def vocabulary(self) -> List[str]:
        return sorted(self.idf)

    def ranked(self, doc_name: str, top: Optional[int] = None) -> List[Tuple[str, float]]:
        rows = sorted(
            self.tfidf[doc_name].items(),
            key=lambda item: (-item[1], item[0]),
        )
        if top is not None:
            return rows[:top]
        return rows

    def vector(self, doc_name: str, vocab: Optional[Sequence[str]] = None) -> List[float]:
        space = vocab if vocab is not None else self.vocabulary
        weights = self.tfidf[doc_name]
        return [weights.get(term, 0.0) for term in space]


def _term_frequency(counts: Mapping[str, int], mode: TFMode) -> Dict[str, float]:
    if mode == "proportion":
        total = sum(counts.values())
        if total == 0:
            return {term: 0.0 for term in counts}
        return {term: n / total for term, n in counts.items()}
    if mode == "log":
        return {term: (1.0 + math.log(n) if n > 0 else 0.0) for term, n in counts.items()}
    raise ValueError(f"unknown tf mode: {mode!r}")


def _inverse_df(n_docs: int, df: int, mode: IDFMode) -> float:
    if df <= 0:
        raise ValueError("df must be positive for terms that appear")
    if mode == "raw":
        return math.log(n_docs / df)
    if mode == "smooth":
        return math.log((n_docs + 1) / (df + 1)) + 1.0
    if mode == "prob":
        if df >= n_docs:
            return 0.0
        return math.log((n_docs - df) / df)
    raise ValueError(f"unknown idf mode: {mode!r}")


def build_model(
    texts: Mapping[str, str],
    *,
    n_docs: Optional[int] = None,
    tf_mode: TFMode = "proportion",
    idf_mode: IDFMode = "raw",
) -> TfidfModel:
    """Tokenize *texts* and compute TF, DF, IDF, and TF-IDF."""
    documents = {name: tokenize(text) for name, text in texts.items()}
    computed_n = len(documents)
    n = computed_n if n_docs is None else n_docs
    if n <= 0:
        raise ValueError("n_docs must be positive")

    df_sets: Dict[str, set] = defaultdict(set)
    raw_counts: Dict[str, Counter] = {}
    for name, tokens in documents.items():
        counts = Counter(tokens)
        raw_counts[name] = counts
        for term in counts:
            df_sets[term].add(name)

    df = {term: len(owners) for term, owners in df_sets.items()}
    idf = {term: _inverse_df(n, df[term], idf_mode) for term in df}

    tf: Dict[str, Dict[str, float]] = {}
    tfidf: Dict[str, Dict[str, float]] = {}
    for name, counts in raw_counts.items():
        tf[name] = _term_frequency(counts, tf_mode)
        tfidf[name] = {term: tf[name][term] * idf[term] for term in counts}

    return TfidfModel(
        documents=documents,
        tf=tf,
        df=df,
        idf=idf,
        tfidf=tfidf,
        n_docs=n,
        tf_mode=tf_mode,
        idf_mode=idf_mode,
    )


def cosine(u: Sequence[float], v: Sequence[float]) -> float:
    if len(u) != len(v):
        raise ValueError("vectors must have the same dimension")
    dot = sum(a * b for a, b in zip(u, v))
    nu = math.sqrt(sum(a * a for a in u))
    nv = math.sqrt(sum(b * b for b in v))
    if nu == 0.0 or nv == 0.0:
        return 0.0
    return dot / (nu * nv)


def pairwise_cosine(model: TfidfModel) -> List[Tuple[str, str, float]]:
    names = sorted(model.tfidf)
    vocab = model.vocabulary
    vectors = {name: model.vector(name, vocab) for name in names}
    pairs: List[Tuple[str, str, float]] = []
    for i, left in enumerate(names):
        for right in names[i + 1 :]:
            pairs.append((left, right, cosine(vectors[left], vectors[right])))
    pairs.sort(key=lambda row: (-row[2], row[0], row[1]))
    return pairs


_LEADING_FLOAT = re.compile(r"^[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?")


def parse_number(value: str) -> float:
    """Parse a TSV score, tolerating the one dirty 2012 IDF cell.

    ``output/idf.txt`` has a single corrupted row, ``thatyou`` →
    ``2.89037175789616y``. The leading float is still ln(18).
    """
    try:
        return float(value)
    except ValueError:
        match = _LEADING_FLOAT.match(value)
        if match is None:
            raise
        return float(match.group(0))


def parse_tsv_scores(path: Path) -> Dict[str, float]:
    """Read a ``term<TAB>number`` file like output/tf or output/tfidf."""
    scores: Dict[str, float] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        term, value = line.split("\t", 1)
        if term == "word" or term.startswith("word "):
            continue
        scores[term] = parse_number(value)
    return scores


def parse_df_table(path: Path) -> Dict[str, Tuple[int, List[str]]]:
    rows: Dict[str, Tuple[int, List[str]]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("word"):
            continue
        parts = line.split("\t")
        term = parts[0]
        df = int(parts[1])
        names = [n.strip() for n in parts[2].split(",") if n.strip()]
        rows[term] = (df, names)
    return rows


def rank_score_map(scores: Mapping[str, float], top: Optional[int] = None) -> List[Tuple[str, float]]:
    rows = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    if top is not None:
        return rows[:top]
    return rows


def format_table(rows: Iterable[Tuple[object, ...]], headers: Sequence[str]) -> str:
    str_rows = [[str(cell) for cell in row] for row in rows]
    widths = [len(h) for h in headers]
    for row in str_rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))
    def fmt(cols: Sequence[str]) -> str:
        return "  ".join(col.ljust(widths[i]) for i, col in enumerate(cols))
    lines = [fmt(headers), fmt(["-" * w for w in widths])]
    lines.extend(fmt(row) for row in str_rows)
    return "\n".join(lines)
