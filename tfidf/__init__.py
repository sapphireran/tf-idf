"""Personal TF-IDF study library. Stdlib only. Not a product."""

from .index import CorpusIndex
from .rank import rank_query
from .tokenize import perl_legacy_tokens, simple_tokens
from .weights import idf as compute_idf
from .weights import tf as compute_tf

__all__ = [
    "CorpusIndex",
    "rank_query",
    "perl_legacy_tokens",
    "simple_tokens",
    "compute_idf",
    "compute_tf",
]
