"""Exact TF-IDF table for examples/micro-corpus (see docs/worked-example.md)."""

from __future__ import annotations

import math
import tempfile
import unittest
from pathlib import Path

from support import MICRO

from tfidf_lib import (
    reconstruct_df,
    score_collection,
    top_terms,
    write_collection,
    read_score_tsv,
)

LN3 = math.log(3)
LN3_OVER_2 = math.log(3 / 2)
SIXTH = 1 / 6
THIRD = 1 / 3


class MicroCorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scores = score_collection(MICRO)
        cls.by_name = {doc.name: doc for doc in cls.scores.documents}

    def test_collection_size_is_three(self) -> None:
        self.assertEqual(self.scores.n_docs, 3)

    def test_document_lengths(self) -> None:
        self.assertEqual(self.by_name["d1-cat.txt"].words, 6)
        self.assertEqual(self.by_name["d2-dog.txt"].words, 6)
        self.assertEqual(self.by_name["d3-bread.txt"].words, 3)

    def test_document_frequencies(self) -> None:
        df = self.scores.df
        for term in ("cat", "mat", "dog", "log", "bake", "bakers", "bread"):
            self.assertEqual(df[term], 1, term)
        for term in ("the", "sat", "on"):
            self.assertEqual(df[term], 2, term)

    def test_idf_values(self) -> None:
        self.assertAlmostEqual(self.scores.idf["cat"], LN3)
        self.assertAlmostEqual(self.scores.idf["the"], LN3_OVER_2)
        self.assertAlmostEqual(self.scores.idf["bread"], LN3)

    def test_reconstruct_df_from_idf(self) -> None:
        for term, df in self.scores.df.items():
            recovered = reconstruct_df(3, self.scores.idf[term])
            self.assertAlmostEqual(recovered, df, places=12)

    def test_tf_d1(self) -> None:
        tf = self.by_name["d1-cat.txt"].tf
        self.assertAlmostEqual(tf["the"], 2 * SIXTH)
        self.assertAlmostEqual(tf["cat"], SIXTH)
        self.assertAlmostEqual(tf["mat"], SIXTH)
        self.assertNotIn("dog", tf)

    def test_tfidf_d1_ranking(self) -> None:
        ranked = top_terms(self.by_name["d1-cat.txt"].tfidf, 5)
        terms = [term for term, _ in ranked]
        self.assertEqual(terms[:2], ["cat", "mat"])
        self.assertAlmostEqual(ranked[0][1], SIXTH * LN3)
        self.assertAlmostEqual(ranked[1][1], SIXTH * LN3)
        self.assertEqual(terms[2], "the")
        self.assertAlmostEqual(ranked[2][1], (2 * SIXTH) * LN3_OVER_2)
        self.assertEqual(set(terms[3:]), {"on", "sat"})

    def test_tfidf_d2_is_symmetric(self) -> None:
        ranked = top_terms(self.by_name["d2-dog.txt"].tfidf, 2)
        self.assertEqual([term for term, _ in ranked], ["dog", "log"])
        self.assertAlmostEqual(ranked[0][1], SIXTH * LN3)
        self.assertAlmostEqual(ranked[1][1], SIXTH * LN3)

    def test_tfidf_d3_short_document_is_loud(self) -> None:
        ranked = top_terms(self.by_name["d3-bread.txt"].tfidf, 3)
        self.assertEqual(
            [term for term, _ in ranked], ["bake", "bakers", "bread"]
        )
        for _, value in ranked:
            self.assertAlmostEqual(value, THIRD * LN3)
        # Every baking term beats every cat-document term.
        cat_best = top_terms(self.by_name["d1-cat.txt"].tfidf, 1)[0][1]
        self.assertGreater(ranked[0][1], cat_best)

    def test_round_trip_tsv_writer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            write_collection(self.scores, out)
            idf = read_score_tsv(out / "idf.txt")
            self.assertAlmostEqual(idf["cat"], LN3)
            tfidf = read_score_tsv(out / "tfidf" / "d1-cat.txt")
            self.assertAlmostEqual(tfidf["cat"], SIXTH * LN3)
            df_text = (out / "df.txt").read_text(encoding="utf-8")
            self.assertTrue(df_text.startswith("word \t #docs it exists in"))
            self.assertIn("d1-cat.txt", df_text)


if __name__ == "__main__":
    unittest.main()
