#!/usr/bin/env python3
"""Unit tests for the teaching TF-IDF example.

Run from the repository root:

    python3 tests/test_tfidf_toy.py
"""

from __future__ import annotations

import math
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "examples"))

import tfidf_toy  # noqa: E402


class TokenizeTests(unittest.TestCase):
    def test_lowercases_and_strips_punctuation(self) -> None:
        tokens = tfidf_toy.tokenize("Hello, ALICE's cat!")
        self.assertEqual(tokens, ["hello", "alices", "cat"])

    def test_keeps_digits(self) -> None:
        tokens = tfidf_toy.tokenize("Psalm 23 is short.")
        self.assertEqual(tokens, ["psalm", "23", "is", "short"])

    def test_skips_empty_tokens(self) -> None:
        tokens = tfidf_toy.tokenize("  ...  --  ")
        self.assertEqual(tokens, [])


class ClassicThreeDocTests(unittest.TestCase):
    """Hand-computable example used in docs/06-hand-worked-example.md."""

    @classmethod
    def setUpClass(cls) -> None:
        corpus = ROOT / "examples" / "classic-three-docs"
        cls.result = tfidf_toy.analyze_corpus(tfidf_toy.load_corpus(corpus))

    def test_document_count(self) -> None:
        self.assertEqual(self.result["n_docs"], 3)

    def test_token_counts(self) -> None:
        tokens = self.result["tokens_by_doc"]
        self.assertEqual(tokens["cat_mat.txt"], ["the", "cat", "sat", "on", "the", "mat"])
        self.assertEqual(tokens["dog_log.txt"], ["the", "dog", "sat", "on", "the", "log"])
        self.assertEqual(
            tokens["friends.txt"], ["cats", "and", "dogs", "are", "friends"]
        )

    def test_normalized_tf_in_cat_mat(self) -> None:
        tf = self.result["tf"]["cat_mat.txt"]
        self.assertAlmostEqual(tf["the"], 2 / 6)
        self.assertAlmostEqual(tf["cat"], 1 / 6)
        self.assertAlmostEqual(tf["mat"], 1 / 6)

    def test_df_values(self) -> None:
        df = self.result["df"]
        self.assertEqual(df["the"], 2)
        self.assertEqual(df["sat"], 2)
        self.assertEqual(df["cat"], 1)
        self.assertEqual(df["friends"], 1)
        self.assertNotIn("the", self.result["tf"]["friends.txt"])

    def test_idf_matches_natural_log(self) -> None:
        idf = self.result["idf"]
        self.assertAlmostEqual(idf["the"], math.log(3 / 2))
        self.assertAlmostEqual(idf["cat"], math.log(3 / 1))
        self.assertAlmostEqual(idf["friends"], math.log(3 / 1))

    def test_cat_outranks_the_in_cat_mat(self) -> None:
        scores = self.result["tfidf"]["cat_mat.txt"]
        self.assertGreater(scores["cat"], scores["the"])
        self.assertGreater(scores["mat"], scores["the"])
        expected_cat = (1 / 6) * math.log(3)
        self.assertAlmostEqual(scores["cat"], expected_cat)

    def test_friends_terms_are_unique(self) -> None:
        scores = self.result["tfidf"]["friends.txt"]
        unique_weight = (1 / 5) * math.log(3)
        for term in ("cats", "and", "dogs", "are", "friends"):
            self.assertAlmostEqual(scores[term], unique_weight)


class TinyCorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        corpus = ROOT / "examples" / "tiny-corpus"
        cls.result = tfidf_toy.analyze_corpus(tfidf_toy.load_corpus(corpus))

    def test_five_documents(self) -> None:
        self.assertEqual(self.result["n_docs"], 5)
        self.assertEqual(
            sorted(self.result["documents"]),
            [
                "garden.txt",
                "harbor.txt",
                "kitchen.txt",
                "stars.txt",
                "workshop.txt",
            ],
        )

    def test_shared_the_has_low_or_zero_idf(self) -> None:
        df = self.result["df"]
        idf = self.result["idf"]
        self.assertEqual(df["the"], 5)
        self.assertAlmostEqual(idf["the"], 0.0)

    def test_distinctive_headwords(self) -> None:
        tops = {
            name: tfidf_toy.top_k(scores, 1)[0][0]
            for name, scores in self.result["tfidf"].items()
        }
        self.assertEqual(tops["kitchen.txt"], "soup")
        self.assertEqual(tops["garden.txt"], "roses")
        self.assertEqual(tops["harbor.txt"], "boat")
        self.assertEqual(tops["workshop.txt"], "oak")
        self.assertEqual(tops["stars.txt"], "hill")

    def test_unique_content_words_share_max_idf(self) -> None:
        idf = self.result["idf"]
        max_idf = math.log(5 / 1)
        self.assertAlmostEqual(idf["soup"], max_idf)
        self.assertAlmostEqual(idf["telescope"], max_idf)
        self.assertAlmostEqual(idf["carpenter"], max_idf)


class RankingAndIdfGuardTests(unittest.TestCase):
    def test_top_k_tie_breaks_alphabetically(self) -> None:
        ranked = tfidf_toy.top_k({"b": 1.0, "a": 1.0, "c": 0.5}, k=2)
        self.assertEqual(ranked, [("a", 1.0), ("b", 1.0)])

    def test_idf_rejects_bad_df(self) -> None:
        with self.assertRaises(ValueError):
            tfidf_toy.inverse_document_frequency({"x": 3}, n_docs=2)

    def test_load_corpus_skips_non_txt(self) -> None:
        corpus = ROOT / "examples" / "tiny-corpus"
        docs = tfidf_toy.load_corpus(corpus)
        self.assertTrue(all(name.endswith(".txt") for name in docs))


if __name__ == "__main__":
    unittest.main()
