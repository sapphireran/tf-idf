"""Toy tf-idf matching the personal Gutenberg Perl scripts in this repo.

Import :class:`TfIdfIndex` for in-memory scoring, or run::

    python3 -m tfidf_toy demo
    python3 -m tfidf_toy top --input gutenberg --k 12
"""

from .model import DocumentModel, TfIdfIndex, idf_value
from .tokenize import load_corpus, tokenize, tokenize_line

__all__ = [
    "DocumentModel",
    "TfIdfIndex",
    "idf_value",
    "load_corpus",
    "tokenize",
    "tokenize_line",
]
