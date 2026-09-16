"""Load the 2012 Gutenberg TF-IDF snapshot as sparse vectors.

Personal helper for the reading-companion notes. Standard library
only. Never writes into ``output/``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

DOC_SUFFIX = ".txt"


def find_root(start: Path | None = None) -> Path:
    """Walk upward until ``output/tfidf`` and ``gutenberg`` both exist."""
    here = (start or Path(__file__).resolve()).resolve()
    if here.is_file():
        here = here.parent
    for candidate in (here, *here.parents):
        if (candidate / "output" / "tfidf").is_dir() and (
            candidate / "gutenberg"
        ).is_dir():
            return candidate
    raise FileNotFoundError(
        "Cannot find repository root (missing output/tfidf or gutenberg)."
    )


def parse_term_score_line(line: str) -> tuple[str, float] | None:
    """Return ``(term, float)`` or None if the row is damaged / blank."""
    raw = line.rstrip("\n")
    if not raw:
        return None
    term, _, score = raw.partition("\t")
    if not score:
        return None
    try:
        return term, float(score)
    except ValueError:
        return None


def load_term_scores(path: Path) -> dict[str, float]:
    weights: dict[str, float] = {}
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            parsed = parse_term_score_line(line)
            if parsed is None:
                continue
            term, score = parsed
            weights[term] = score
    return weights


def l2_norm(vector: dict[str, float]) -> float:
    return math.sqrt(sum(value * value for value in vector.values()))


def cosine(left: dict[str, float], right: dict[str, float]) -> float:
    if not left or not right:
        return 0.0
    # Iterate the smaller dict. Snapshot files are already sparse.
    if len(left) > len(right):
        left, right = right, left
    dot = sum(weight * right.get(term, 0.0) for term, weight in left.items())
    denom = l2_norm(left) * l2_norm(right)
    if denom == 0.0:
        return 0.0
    return dot / denom


def query_vector(tokens: Iterable[str]) -> dict[str, float]:
    counts: dict[str, float] = {}
    for token in tokens:
        word = token.lower()
        if not word:
            continue
        counts[word] = counts.get(word, 0.0) + 1.0
    return counts


@dataclass(frozen=True)
class Shelf:
    """In-memory view of ``output/tfidf`` plus optional raw word counts."""

    root: Path
    tfidf: dict[str, dict[str, float]]
    norms: dict[str, float]

    @classmethod
    def load(cls, root: Path | None = None) -> "Shelf":
        base = find_root(root) if root is None else Path(root)
        folder = base / "output" / "tfidf"
        tfidf: dict[str, dict[str, float]] = {}
        for path in sorted(folder.glob(f"*{DOC_SUFFIX}")):
            if path.name.startswith("."):
                continue
            tfidf[path.name] = load_term_scores(path)
        if not tfidf:
            raise FileNotFoundError(f"No TF-IDF tables under {folder}")
        norms = {name: l2_norm(vec) for name, vec in tfidf.items()}
        return cls(root=base, tfidf=tfidf, norms=norms)

    @property
    def documents(self) -> list[str]:
        return list(self.tfidf)

    def short_name(self, filename: str) -> str:
        return filename.removesuffix(DOC_SUFFIX)

    def pair_cosine(self, left: str, right: str) -> float:
        if left == right:
            return 1.0
        return cosine(self.tfidf[left], self.tfidf[right])

    def pairwise(self) -> list[tuple[float, str, str]]:
        names = self.documents
        pairs: list[tuple[float, str, str]] = []
        for i, left in enumerate(names):
            for right in names[i + 1 :]:
                pairs.append((self.pair_cosine(left, right), left, right))
        pairs.sort(reverse=True)
        return pairs

    def neighbors(self, filename: str, k: int = 2) -> list[tuple[float, str]]:
        ranked = [
            (self.pair_cosine(filename, other), other)
            for other in self.documents
            if other != filename
        ]
        ranked.sort(reverse=True)
        return ranked[:k]

    def group_mean(self, filenames: Iterable[str]) -> float:
        names = list(filenames)
        scores = [
            self.pair_cosine(left, right)
            for i, left in enumerate(names)
            for right in names[i + 1 :]
        ]
        if not scores:
            return 0.0
        return sum(scores) / len(scores)

    def rank_query(self, tokens: Iterable[str]) -> list[tuple[float, str]]:
        query = query_vector(tokens)
        qn = l2_norm(query)
        ranked: list[tuple[float, str]] = []
        for name, vector in self.tfidf.items():
            dn = self.norms[name]
            if qn == 0.0 or dn == 0.0:
                ranked.append((0.0, name))
                continue
            dot = sum(count * vector.get(term, 0.0) for term, count in query.items())
            ranked.append((dot / (qn * dn), name))
        ranked.sort(reverse=True)
        return ranked

    def top_terms(self, filename: str, n: int = 15) -> list[tuple[str, float]]:
        items = sorted(
            self.tfidf[filename].items(), key=lambda kv: (-kv[1], kv[0])
        )
        return items[:n]

    def heaviest_term(self, filename: str) -> tuple[str, float]:
        tops = self.top_terms(filename, n=1)
        if not tops:
            raise ValueError(f"No terms in {filename}")
        return tops[0]

    def raw_word_count(self, filename: str) -> int:
        path = self.root / "gutenberg" / filename
        text = path.read_text(encoding="utf-8", errors="replace")
        return len(text.split())

    def load_idf(self) -> dict[str, float]:
        return load_term_scores(self.root / "output" / "idf.txt")

    def load_tf(self, filename: str) -> dict[str, float]:
        return load_term_scores(self.root / "output" / "tf" / filename)

    def documents_containing(self, term: str) -> list[str]:
        return [name for name, vec in self.tfidf.items() if vec.get(term, 0.0) != 0.0]
