"""Personal study kit for changing the *document unit* of this TF-IDF toy.

The 2012 Perl scripts treat each Gutenberg file as one document. That is a
reasonable first pass and a poor last one: *Alice* is twelve chapters, the
King James text is a shelf of books, and Macbeth is a stack of speaking
voices. This package keeps the original snapshot untouched and recomputes
the same ``tf * ln(N/df)`` product on those smaller units, plus a handful
of original commonplace-book notes.
"""

from .index import Document, TfIdfIndex
from .retrieve import Passage, rank_passages, window_passages
from .tokenize import tokenize, tokenize_perl
from .weights import idf_classic, tf_normalized, tfidf_classic

__all__ = [
    "Document",
    "Passage",
    "TfIdfIndex",
    "idf_classic",
    "rank_passages",
    "tf_normalized",
    "tfidf_classic",
    "tokenize",
    "tokenize_perl",
    "window_passages",
]

__version__ = "0.1.0"
