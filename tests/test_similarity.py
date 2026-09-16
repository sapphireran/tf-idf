"""Dot product and cosine edge cases."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tests.support import PYTHON_EXAMPLES  # noqa: F401
from tfidfkit.similarity import boolean_vector, cosine, dot, query_vector
from tfidfkit.weights import compute_idf


class SimilarityTests(unittest.TestCase):
    def test_orthogonal_when_only_shared_weight_is_zero(self) -> None:
        left = {"chase": 0.0, "mice": 1.0}
        right = {"chase": 0.0, "birds": 1.0}
        self.assertEqual(dot(left, right), 0.0)
        self.assertEqual(cosine(left, right), 0.0)

    def test_identical_vectors_have_cosine_one(self) -> None:
        vector = {"dogs": 0.3, "mats": 0.05}
        self.assertAlmostEqual(cosine(vector, vector), 1.0)

    def test_empty_vector_is_zero(self) -> None:
        self.assertEqual(cosine({}, {"a": 1.0}), 0.0)

    def test_boolean_vector_drops_zeros(self) -> None:
        self.assertEqual(boolean_vector({"a": 0.4, "the": 0.0}), {"a": 1.0})

    def test_query_uses_corpus_idf_not_query_df(self) -> None:
        idf = compute_idf({"alice": {"d1"}, "the": {"d1", "d2", "d3"}}, 3)
        weights = query_vector("alice the alice", idf)
        self.assertIn("alice", weights)
        self.assertEqual(weights["the"], 0.0)
        self.assertGreater(weights["alice"], 0.0)


if __name__ == "__main__":
    unittest.main()
