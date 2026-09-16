"""In-memory TF-IDF index for a list of personal study documents."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Literal, Sequence

from .tokenize import token_counts, tokenize, tokenize_perl
from .weights import cosine, idf_classic, idf_smooth, tf_normalized

IdfMode = Literal["classic", "smooth"]
TokenMode = Literal["study", "perl"]


@dataclass(frozen=True)
class Document:
    doc_id: str
    title: str
    text: str
    source: str = ""
    tokens: tuple[str, ...] = field(default_factory=tuple)
    word_count: int = 0

    def with_tokens(self, mode: TokenMode = "study") -> "Document":
        if mode == "perl":
            tokens, word_count = tokenize_perl(self.text)
        else:
            tokens = tokenize(self.text)
            word_count = len(tokens)
        return Document(
            doc_id=self.doc_id,
            title=self.title,
            text=self.text,
            source=self.source,
            tokens=tuple(tokens),
            word_count=word_count,
        )


class TfIdfIndex:
    """Classic or smoothed TF-IDF over an in-memory document list."""

    def __init__(
        self,
        documents: Sequence[Document],
        *,
        idf_mode: IdfMode = "classic",
        token_mode: TokenMode = "study",
    ) -> None:
        self.idf_mode = idf_mode
        self.token_mode = token_mode
        self.documents = [doc.with_tokens(token_mode) for doc in documents]
        self.n_docs = len(self.documents)
        if self.n_docs == 0:
            raise ValueError("TfIdfIndex needs at least one document")

        self.df: dict[str, int] = {}
        for doc in self.documents:
            for term in set(doc.tokens):
                self.df[term] = self.df.get(term, 0) + 1

        idf_fn = idf_smooth if idf_mode == "smooth" else idf_classic
        self.idf = {term: idf_fn(self.n_docs, df) for term, df in self.df.items()}

        self._tfidf: dict[str, dict[str, float]] = {}
        self._by_id = {doc.doc_id: doc for doc in self.documents}
        for doc in self.documents:
            counts = token_counts(doc.tokens)
            weights: dict[str, float] = {}
            for term, count in counts.items():
                idf = self.idf[term]
                if idf == 0.0:
                    continue
                weights[term] = tf_normalized(count, doc.word_count) * idf
            self._tfidf[doc.doc_id] = weights

    def document(self, doc_id: str) -> Document:
        return self._by_id[doc_id]

    def vector(self, doc_id: str) -> dict[str, float]:
        return self._tfidf[doc_id]

    def top_terms(self, doc_id: str, k: int = 8) -> list[tuple[str, float]]:
        items = sorted(self._tfidf[doc_id].items(), key=lambda kv: (-kv[1], kv[0]))
        return items[:k]

    def query_vector(self, text: str) -> dict[str, float]:
        if self.token_mode == "perl":
            tokens, word_count = tokenize_perl(text)
        else:
            tokens = tokenize(text)
            word_count = len(tokens)
        counts = token_counts(tokens)
        weights: dict[str, float] = {}
        for term, count in counts.items():
            idf = self.idf.get(term)
            if not idf:
                continue
            weights[term] = tf_normalized(count, word_count) * idf
        return weights

    def rank(self, query: str, k: int = 5) -> list[tuple[Document, float]]:
        qv = self.query_vector(query)
        scored = [
            (doc, cosine(qv, self._tfidf[doc.doc_id])) for doc in self.documents
        ]
        scored.sort(key=lambda item: (-item[1], item[0].doc_id))
        return scored[:k]

    def distinctive_overlap(
        self, left_id: str, right_id: str, k: int = 8
    ) -> list[tuple[str, float, float]]:
        """Terms with a large |tfidf_left - tfidf_right| gap."""
        left = self._tfidf[left_id]
        right = self._tfidf[right_id]
        terms = set(left) | set(right)
        gaps = []
        for term in terms:
            lv = left.get(term, 0.0)
            rv = right.get(term, 0.0)
            gaps.append((term, lv, rv, abs(lv - rv)))
        gaps.sort(key=lambda row: (-row[3], row[0]))
        return [(term, lv, rv) for term, lv, rv, _ in gaps[:k]]


def index_from_pairs(
    pairs: Iterable[tuple[str, str, str]],
    *,
    idf_mode: IdfMode = "classic",
    token_mode: TokenMode = "study",
    source: str = "",
) -> TfIdfIndex:
    docs = [
        Document(doc_id=doc_id, title=title, text=text, source=source)
        for doc_id, title, text in pairs
    ]
    return TfIdfIndex(docs, idf_mode=idf_mode, token_mode=token_mode)
