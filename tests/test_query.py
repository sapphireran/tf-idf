"""Query ranking and attribution against field notes and Gutenberg gold."""

from __future__ import annotations

import unittest
from pathlib import Path

from querydesk.index import build_index, load_committed_index
from querydesk.query import explain, rank

ROOT = Path(__file__).resolve().parent.parent


class FieldQueryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.index = build_index(ROOT / "examples" / "field-notes" / "texts")

    def test_explain_only_query_terms(self) -> None:
        _, rows = explain("cairn icefall", self.index, "glacier-cairn.txt", top=20)
        terms = {row.term for row in rows if row.product > 0}
        self.assertEqual(terms, {"cairn", "icefall"})
        self.assertNotIn("hut", terms)

    def test_miss_has_zero_cosine(self) -> None:
        score, rows = explain("cairn", self.index, "tide-gauge.txt")
        self.assertEqual(score, 0.0)
        self.assertTrue(all(row.product == 0.0 for row in rows))


class GutenbergGoldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.committed = load_committed_index(ROOT / "output")
        cls.built = build_index(ROOT / "gutenberg", n_mode="texts")

    def test_committed_n_is_eighteen(self) -> None:
        self.assertEqual(self.committed.n, 18)
        self.assertEqual(self.built.n, 18)

    def test_alice_idf_bucket(self) -> None:
        self.assertEqual(self.built.df["alice"], 3)
        self.assertAlmostEqual(self.built.idf["alice"], self.committed.idf["alice"])
        self.assertAlmostEqual(self.committed.idf["alice"], 1.79175946922805, places=12)

    def test_zero_idf_the(self) -> None:
        self.assertEqual(self.committed.idf["the"], 0.0)
        alice = self.committed.docs["carroll-alice.txt"]
        self.assertEqual(alice.tfidf["the"], 0.0)

    def test_whale_query_prefers_moby_dick(self) -> None:
        hits = rank("white whale pequod ahab", self.built, score="cosine", top=3)
        self.assertEqual(hits[0].name, "melville-moby_dick.txt")
        self.assertGreater(hits[0].score, hits[1].score)

    def test_gryphon_query_prefers_alice(self) -> None:
        hits = rank("gryphon dormouse hatter", self.built, score="cosine", top=1)
        self.assertEqual(hits[0].name, "carroll-alice.txt")

    def test_explain_whale_features_overlap_only(self) -> None:
        _, rows = explain(
            "white whale pequod ahab",
            self.built,
            "melville-moby_dick.txt",
            top=8,
        )
        terms = [row.term for row in rows]
        self.assertTrue(set(terms) <= {"white", "whale", "pequod", "ahab"})
        self.assertIn("whale", terms)
        self.assertIn("ahab", terms)
