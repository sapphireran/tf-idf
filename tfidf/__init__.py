"""Educational TF-IDF toolkit for this personal Gutenberg toy repo.

The formulas match the original Perl scripts in spirit:

    tf(t, d)  = count(t, d) / tokens(d)
    idf(t)    = log(N / df(t))          # natural log, "raw" mode
    tfidf     = tf * idf

A sklearn-style smoothed IDF is available for comparison. See
``docs/algorithm.md`` for the arithmetic and the Perl quirks.
"""

from .compute import DocumentVector, TfidfIndex, build_index, score_query
from .io_tsv import read_weight_table, write_pipeline_output
from .tokenize import normalize_text, tokenize, tokenize_document

__all__ = [
    "DocumentVector",
    "TfidfIndex",
    "build_index",
    "normalize_text",
    "read_weight_table",
    "score_query",
    "tokenize",
    "tokenize_document",
    "write_pipeline_output",
]

__version__ = "0.2.0"
