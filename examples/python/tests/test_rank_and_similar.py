"""Ranking and cosine checks, including reading committed Gutenberg tables."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

_EXAMPLES_PYTHON = Path(__file__).resolve().parents[1]
_REPO_ROOT = _EXAMPLES_PYTHON.parents[1]
if str(_EXAMPLES_PYTHON) not in sys.path:
    sys.path.insert(0, str(_EXAMPLES_PYTHON))

from similar_docs import cosine, pairwise_cosine  # noqa: E402
from tfidf_toy import load_weight_table, ranked_terms, score_corpus  # noqa: E402


TINY = _REPO_ROOT / "examples" / "tiny-corpus" / "documents"
ALICE_TABLE = _REPO_ROOT / "output" / "tfidf" / "carroll-alice.txt"
MOBY_TABLE = _REPO_ROOT / "output" / "tfidf" / "melville-moby_dick.txt"
IDF_TABLE = _REPO_ROOT / "output" / "idf.txt"


class RankTests(unittest.TestCase):
    def test_tie_breaks_alphabetically(self) -> None:
        ranked = ranked_terms({"b": 1.0, "a": 1.0, "c": 0.5}, top=3)
        self.assertEqual([token for token, _ in ranked], ["a", "b", "c"])

    def test_committed_alice_top_is_alice(self) -> None:
        weights = load_weight_table(ALICE_TABLE)
        top = ranked_terms(weights, top=8)
        self.assertEqual(top[0][0], "alice")
        self.assertGreater(top[0][1], 0.02)
        names = [token for token, _ in top]
        for expected in ("gryphon", "dormouse", "duchess", "hatter"):
            self.assertIn(expected, names)

    def test_committed_moby_top_is_whale(self) -> None:
        weights = load_weight_table(MOBY_TABLE)
        self.assertEqual(ranked_terms(weights, top=1)[0][0], "whale")

    def test_corrupt_idf_line_is_skipped(self) -> None:
        weights = load_weight_table(IDF_TABLE)
        self.assertNotIn("thatyou", weights)
        self.assertEqual(weights["the"], 0.0)
        self.assertAlmostEqual(weights["macbeth"], math.log(18), places=10)
        self.assertAlmostEqual(weights["alice"], math.log(6), places=10)


class CosineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tables = {doc.name: doc.tfidf for doc in score_corpus(TINY).documents}

    def test_bakery_pair_is_closest(self) -> None:
        pairs = pairwise_cosine(self.tables)
        top_left, top_right, top_score = pairs[0]
        self.assertEqual(
            {top_left, top_right},
            {"01-bakery-morning.txt", "03-bakery-afternoon.txt"},
        )
        self.assertAlmostEqual(top_score, 0.250872603002, places=9)

    def test_orthogonal_pairs_are_zero(self) -> None:
        tables = self.tables
        self.assertEqual(cosine(tables["01-bakery-morning.txt"], tables["02-ridge-trail.txt"]), 0.0)
        self.assertEqual(cosine(tables["01-bakery-morning.txt"], tables["04-rehearsal-room.txt"]), 0.0)
        self.assertEqual(cosine(tables["02-ridge-trail.txt"], tables["03-bakery-afternoon.txt"]), 0.0)

    def test_identical_vectors_cosine_one(self) -> None:
        vec = {"bread": 0.2, "baker": 0.1}
        self.assertAlmostEqual(cosine(vec, vec), 1.0, places=12)

    def test_empty_vector_is_zero(self) -> None:
        self.assertEqual(cosine({}, {"a": 1.0}), 0.0)


if __name__ == "__main__":
    unittest.main()
