"""In-memory corpus index for the personal TF-IDF lab."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from . import stopwords as stopword_mod
from .tokenize import drop_stopwords, tokenize
from .weights import document_weights, idf

DEFAULT_TINY = Path(__file__).resolve().parent.parent / "examples" / "tiny_corpus"
DEFAULT_GUTENBERG = Path(__file__).resolve().parent.parent / "gutenberg"


@dataclass
class Document:
    name: str
    path: Optional[Path]
    tokens: List[str]
    counts: Counter
    length: int


@dataclass
class CorpusIndex:
    documents: List[Document]
    tokenizer: str = "simple"
    df: Dict[str, int] = field(default_factory=dict)
    postings: Dict[str, List[str]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self._rebuild_stats()

    def _rebuild_stats(self) -> None:
        df: Dict[str, int] = {}
        postings: Dict[str, List[str]] = defaultdict(list)
        for doc in self.documents:
            for term in doc.counts:
                df[term] = df.get(term, 0) + 1
                postings[term].append(doc.name)
        self.df = df
        self.postings = dict(postings)

    @property
    def n_docs(self) -> int:
        return len(self.documents)

    @property
    def avgdl(self) -> float:
        if not self.documents:
            return 0.0
        return sum(d.length for d in self.documents) / float(len(self.documents))

    def document(self, name: str) -> Document:
        for doc in self.documents:
            if doc.name == name or (doc.path and str(doc.path) == name):
                return doc
            if doc.path and doc.path.name == Path(name).name:
                return doc
        raise KeyError(f"no document named {name!r}")

    def idf_table(self, flavor: str = "classic") -> Dict[str, float]:
        return {term: idf(df, self.n_docs, flavor) for term, df in self.df.items()}

    def weights_for(
        self,
        name: str,
        *,
        idf_flavor: str = "classic",
        tf_flavor: str = "normalized",
    ) -> Dict[str, float]:
        doc = self.document(name)
        return document_weights(
            doc.counts,
            doc.length,
            self.idf_table(idf_flavor),
            tf_flavor=tf_flavor,
            avgdl=self.avgdl,
        )

    def top_terms(
        self,
        name: str,
        k: int = 10,
        *,
        idf_flavor: str = "classic",
        tf_flavor: str = "normalized",
        alpha_only: bool = False,
    ) -> List[Tuple[str, float]]:
        weights = self.weights_for(name, idf_flavor=idf_flavor, tf_flavor=tf_flavor)
        items = list(weights.items())
        if alpha_only:
            items = [(t, w) for t, w in items if t.isalpha()]
        items.sort(key=lambda pair: (-pair[1], pair[0]))
        return items[:k]

    def corpus_stats(self) -> List[Tuple[str, int, int]]:
        """Return (name, token_length, unique_terms) rows."""
        rows = [(d.name, d.length, len(d.counts)) for d in self.documents]
        rows.sort(key=lambda row: (-row[1], row[0]))
        return rows

    @classmethod
    def from_texts(
        cls,
        texts: Mapping[str, str],
        *,
        tokenizer: str = "simple",
        use_stopwords: bool = False,
        extra_stopwords: Optional[Iterable[str]] = None,
    ) -> "CorpusIndex":
        banned = set()
        if use_stopwords:
            banned.update(stopword_mod.ENGLISH_STUDY)
        if extra_stopwords:
            banned.update(s.lower() for s in extra_stopwords)
        documents: List[Document] = []
        for name, text in texts.items():
            tokens, length = tokenize(text, tokenizer=tokenizer)
            if banned:
                tokens = drop_stopwords(tokens, banned)
                if tokenizer == "simple":
                    length = len(tokens)
            documents.append(
                Document(
                    name=name,
                    path=None,
                    tokens=tokens,
                    counts=Counter(tokens),
                    length=length,
                )
            )
        documents.sort(key=lambda d: d.name)
        return cls(documents=documents, tokenizer=tokenizer)

    @classmethod
    def from_directory(
        cls,
        directory: Path,
        *,
        tokenizer: str = "simple",
        glob: str = "*.txt",
        use_stopwords: bool = False,
        extra_stopwords: Optional[Iterable[str]] = None,
    ) -> "CorpusIndex":
        directory = Path(directory)
        texts: Dict[str, str] = {}
        paths: Dict[str, Path] = {}
        for path in sorted(directory.glob(glob)):
            if path.name.startswith("."):
                continue
            texts[path.name] = path.read_text(encoding="utf-8", errors="replace")
            paths[path.name] = path
        index = cls.from_texts(
            texts,
            tokenizer=tokenizer,
            use_stopwords=use_stopwords,
            extra_stopwords=extra_stopwords,
        )
        for doc in index.documents:
            doc.path = paths.get(doc.name)
        return index


def resolve_corpus(name: str) -> Path:
    key = name.strip().lower()
    if key in {"tiny", "tiny_corpus", "example", "examples"}:
        return DEFAULT_TINY
    if key in {"gutenberg", "gut", "books", "shelf"}:
        return DEFAULT_GUTENBERG
    path = Path(name)
    if path.is_dir():
        return path
    raise FileNotFoundError(
        f"unknown corpus {name!r}; use 'tiny', 'gutenberg', or a directory"
    )
