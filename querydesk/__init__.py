"""Personal query desk for the 2012 Gutenberg TF-IDF toy.

Standard-library only. Default weights match the checked-in tables:
normalized TF × ln(N / df) with N = number of non-hidden text files.
"""

from .index import Index, build_index, load_committed_index
from .query import Attribution, Hit, compare_rankings, explain, rank
from .tokenize import count_document, count_path, normalize_line, split_fields
from .weights import idf_map, idf_value, normalized_tf, tfidf_map

__all__ = [
    "Attribution",
    "Hit",
    "Index",
    "build_index",
    "compare_rankings",
    "count_document",
    "count_path",
    "explain",
    "idf_map",
    "idf_value",
    "load_committed_index",
    "normalize_line",
    "normalized_tf",
    "rank",
    "split_fields",
    "tfidf_map",
]
