"""Ranking tests for the paragraph-length cats / dogs / baking example."""

from __future__ import annotations

import unittest

from support import TINY

from tfidf_lib import score_collection, top_terms


class TinyCorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scores = score_collection(TINY)
        cls.by_name = {doc.name: doc for doc in cls.scores.documents}

    def test_three_documents(self) -> None:
        self.assertEqual(self.scores.n_docs, 3)
        self.assertEqual(
            set(self.by_name),
            {"cats.txt", "dogs.txt", "baking.txt"},
        )

    def test_shared_template_words_have_df_of_two(self) -> None:
        # Written into both animal paragraphs on purpose.
        for term in ("sun", "nap", "soft", "fur", "afternoon", "happy"):
            self.assertEqual(self.scores.df[term], 2, term)
            self.assertGreater(self.scores.idf[term], 0)

    def test_kitchen_words_are_unique_to_baking(self) -> None:
        for term in ("bread", "dough", "flour", "ovens"):
            self.assertEqual(self.scores.df[term], 1, term)
            self.assertNotIn(term, self.by_name["cats.txt"].tf)
            self.assertNotIn(term, self.by_name["dogs.txt"].tf)

    def test_cats_distinctive_terms_outrank_shared_and_foreign(self) -> None:
        ranked = [term for term, _ in top_terms(self.by_name["cats.txt"].tfidf, 8)]
        self.assertTrue({"cats", "cat", "purr", "yarn"} <= set(ranked))
        self.assertNotIn("bread", ranked)
        self.assertNotIn("bark", ranked)
        self.assertNotIn("ovens", ranked)

    def test_dogs_distinctive_terms_outrank_shared_and_foreign(self) -> None:
        ranked = [term for term, _ in top_terms(self.by_name["dogs.txt"].tfidf, 8)]
        self.assertTrue({"dogs", "dog", "bark"} <= set(ranked))
        self.assertNotIn("yarn", ranked)
        self.assertNotIn("bread", ranked)
        self.assertNotIn("whiskers", ranked)

    def test_baking_distinctive_terms_outrank_animals(self) -> None:
        ranked = [term for term, _ in top_terms(self.by_name["baking.txt"].tfidf, 8)]
        self.assertTrue({"bread", "dough", "flour", "ovens"} <= set(ranked))
        self.assertNotIn("cats", ranked)
        self.assertNotIn("dogs", ranked)
        self.assertNotIn("yarn", ranked)

    def test_collection_wide_absence_means_positive_idf_for_the(self) -> None:
        # "the" appears in all three paragraphs, so IDF is zero — same
        # rule as "a" in the Gutenberg snapshot.
        self.assertIn("the", self.scores.df)
        self.assertEqual(self.scores.df["the"], 3)
        self.assertEqual(self.scores.idf["the"], 0)
        for doc in self.scores.documents:
            if "the" in doc.tfidf:
                self.assertEqual(doc.tfidf["the"], 0)
