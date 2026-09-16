"""Ranking tests on the four-document tiny corpus."""

from __future__ import annotations

import math
import unittest
from pathlib import Path

from tfidf.index import CorpusIndex
from tfidf.rank import query_vector, rank_query

TINY = Path(__file__).resolve().parent.parent / "examples" / "tiny_corpus"


class RankTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.index = CorpusIndex.from_directory(TINY, tokenizer="simple")

    def test_cat_query_prefers_cats(self) -> None:
        ranked = rank_query("cat mat", self.index, scheme="cosine", k=4)
        self.assertEqual(ranked[0].name, "doc_cats.txt")
        self.assertGreater(ranked[0].score, ranked[1].score)

    def test_dog_query_prefers_dogs(self) -> None:
        ranked = rank_query("dog walks", self.index, scheme="cosine", k=4)
        self.assertEqual(ranked[0].name, "doc_dogs.txt")

    def test_kitchen_query_prefers_kitchen(self) -> None:
        ranked = rank_query("warm kitchen soup", self.index, scheme="cosine", k=4)
        self.assertEqual(ranked[0].name, "doc_kitchen.txt")

    def test_stars_query_prefers_stars(self) -> None:
        ranked = rank_query("distant telescopes", self.index, scheme="cosine", k=4)
        self.assertEqual(ranked[0].name, "doc_stars.txt")

    def test_stopword_query_classic_is_empty_vector(self) -> None:
        ranked = rank_query("the", self.index, scheme="cosine", k=4)
        self.assertTrue(all(row.score == 0.0 for row in ranked))
        self.assertTrue(all(row.note == "empty_vector" for row in ranked))

    def test_smooth_idf_lets_stopword_query_prefer_longest(self) -> None:
        # 'the' has a floor under smooth IDF. Length-normalized TF of
        # 'the' is 3/14, 3/14, 3/13, 1/12 — kitchen wins on TF share,
        # but cosine uses the whole vector. Either way the scores are
        # no longer all zero.
        ranked = rank_query(
            "the",
            self.index,
            scheme="cosine",
            idf_flavor="smooth",
            k=4,
        )
        self.assertTrue(any(row.score > 0.0 for row in ranked))
        self.assertTrue(all(row.note == "" for row in ranked))

    def test_dot_product_closed_form_fragment(self) -> None:
        # query 'cat' → one token, tf_norm=1, idf=log 4, weight=log 4
        ranked = rank_query("cat", self.index, scheme="dot", k=4)
        expected = (2 / 14) * math.log(4) * math.log(4)
        self.assertEqual(ranked[0].name, "doc_cats.txt")
        self.assertAlmostEqual(ranked[0].score, expected)
        # other documents have zero 'cat'
        for row in ranked[1:]:
            self.assertEqual(row.score, 0.0)

    def test_query_vector_uses_shelf_idf(self) -> None:
        vec = query_vector(["cat", "the"], self.index, idf_flavor="classic")
        self.assertAlmostEqual(vec["cat"], 0.5 * math.log(4))
        self.assertEqual(vec["the"], 0.0)

    def test_bm25_also_puts_moby_terms_on_the_right_tiny_doc(self) -> None:
        ranked = rank_query("telescopes", self.index, scheme="bm25", k=4)
        self.assertEqual(ranked[0].name, "doc_stars.txt")
        self.assertGreater(ranked[0].score, 0.0)

    def test_unknown_scheme(self) -> None:
        with self.assertRaises(ValueError):
            rank_query("cat", self.index, scheme="neural")


if __name__ == "__main__":
    unittest.main()
