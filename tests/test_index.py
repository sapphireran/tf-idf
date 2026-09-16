"""Tiny-corpus index tests. Counts were done on paper."""

from __future__ import annotations

import math
import unittest
from pathlib import Path

from tfidf.index import CorpusIndex, resolve_corpus

TINY = Path(__file__).resolve().parent.parent / "examples" / "tiny_corpus"


class TinyCorpusIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.index = CorpusIndex.from_directory(TINY, tokenizer="simple")

    def test_four_documents(self) -> None:
        self.assertEqual(self.index.n_docs, 4)
        names = [d.name for d in self.index.documents]
        self.assertEqual(
            names,
            ["doc_cats.txt", "doc_dogs.txt", "doc_kitchen.txt", "doc_stars.txt"],
        )

    def test_lengths(self) -> None:
        self.assertEqual(self.index.document("doc_cats.txt").length, 14)
        self.assertEqual(self.index.document("doc_dogs.txt").length, 14)
        self.assertEqual(self.index.document("doc_kitchen.txt").length, 13)
        self.assertEqual(self.index.document("doc_stars.txt").length, 12)

    def test_raw_counts_cats(self) -> None:
        counts = self.index.document("doc_cats.txt").counts
        self.assertEqual(counts["the"], 3)
        self.assertEqual(counts["cat"], 2)
        self.assertEqual(counts["mat"], 1)
        self.assertEqual(counts["rooms"], 1)

    def test_document_frequencies(self) -> None:
        self.assertEqual(self.index.df["the"], 4)
        self.assertEqual(self.index.df["sat"], 3)
        self.assertEqual(self.index.df["and"], 3)
        self.assertEqual(self.index.df["likes"], 2)
        self.assertEqual(self.index.df["warm"], 2)
        self.assertEqual(self.index.df["quiet"], 2)
        self.assertEqual(self.index.df["fields"], 2)
        self.assertEqual(self.index.df["on"], 2)
        self.assertEqual(self.index.df["cat"], 1)
        self.assertEqual(self.index.df["dog"], 1)
        self.assertEqual(self.index.df["telescopes"], 1)
        self.assertNotIn("elephant", self.index.df)

    def test_classic_idf(self) -> None:
        table = self.index.idf_table("classic")
        self.assertEqual(table["the"], 0.0)
        self.assertAlmostEqual(table["sat"], math.log(4 / 3))
        self.assertAlmostEqual(table["cat"], math.log(4))

    def test_cat_tfidf(self) -> None:
        weights = self.index.weights_for("doc_cats.txt")
        self.assertAlmostEqual(weights["cat"], (2 / 14) * math.log(4))
        self.assertAlmostEqual(weights["the"], 0.0)
        self.assertAlmostEqual(weights["mat"], (1 / 14) * math.log(4))

    def test_top_term_is_distinctive(self) -> None:
        top = self.index.top_terms("doc_cats.txt", k=1)
        self.assertEqual(top[0][0], "cat")
        top_stars = self.index.top_terms("doc_stars.txt", k=3)
        terms = [t for t, _ in top_stars]
        self.assertTrue(set(terms) & {"stars", "telescopes", "night", "light", "faint"})

    def test_resolve_corpus(self) -> None:
        self.assertEqual(resolve_corpus("tiny"), TINY)
        with self.assertRaises(FileNotFoundError):
            resolve_corpus("workplace-logs")


if __name__ == "__main__":
    unittest.main()
