"""Closed-form TF / IDF tests."""

from __future__ import annotations

import math
import unittest

from tfidf.weights import idf, tf, tfidf


class TfTests(unittest.TestCase):
    def test_normalized(self) -> None:
        self.assertAlmostEqual(tf(2, 14, "normalized"), 2 / 14)

    def test_normalized_empty_doc(self) -> None:
        self.assertEqual(tf(0, 0, "normalized"), 0.0)

    def test_raw_log_boolean(self) -> None:
        self.assertEqual(tf(5, 10, "raw"), 5.0)
        self.assertAlmostEqual(tf(5, 10, "log"), 1.0 + math.log(5))
        self.assertEqual(tf(5, 10, "boolean"), 1.0)
        self.assertEqual(tf(0, 10, "log"), 0.0)
        self.assertEqual(tf(0, 10, "boolean"), 0.0)

    def test_augmented(self) -> None:
        self.assertAlmostEqual(tf(2, 14, "augmented", max_count=4), 0.5 + 0.5 * 0.5)

    def test_bm25_no_length_norm_when_avgdl_missing(self) -> None:
        # avgdl == 0 → length_norm = 1, so tf = f*(k1+1) / (f+k1)
        k1 = 1.2
        expected = (3 * (k1 + 1.0)) / (3 + k1)
        self.assertAlmostEqual(tf(3, 100, "bm25", k1=k1, b=0.75), expected)

    def test_unknown_flavor(self) -> None:
        with self.assertRaises(ValueError):
            tf(1, 1, "mystery")


class IdfTests(unittest.TestCase):
    def test_classic_edges(self) -> None:
        self.assertAlmostEqual(idf(1, 18, "classic"), math.log(18))
        self.assertEqual(idf(18, 18, "classic"), 0.0)
        self.assertEqual(idf(0, 18, "classic"), 0.0)

    def test_classic_matches_historical_hapax_stamp(self) -> None:
        # output/idf.txt hapax lines are log(18) ≈ 2.89037175789616
        self.assertAlmostEqual(idf(1, 18, "classic"), 2.89037175789616, places=12)

    def test_smooth_floor_on_collection_term(self) -> None:
        self.assertAlmostEqual(idf(18, 18, "smooth"), 1.0)

    def test_smooth_unseen_is_zero_by_lab_policy(self) -> None:
        self.assertEqual(idf(0, 18, "smooth"), 0.0)

    def test_probabilistic_sign_flip(self) -> None:
        # df < N/2 → positive; df > N/2 → negative; df == N → clamped 0
        self.assertGreater(idf(1, 4, "probabilistic"), 0.0)
        self.assertLess(idf(3, 4, "probabilistic"), 0.0)
        self.assertEqual(idf(4, 4, "probabilistic"), 0.0)
        self.assertAlmostEqual(idf(1, 4, "probabilistic"), math.log(3 / 1))

    def test_bm25_positive_on_collection_term(self) -> None:
        value = idf(18, 18, "bm25")
        self.assertGreater(value, 0.0)
        self.assertAlmostEqual(value, math.log(0.5 / 18.5) + 1.0)

    def test_rejects_df_above_n(self) -> None:
        with self.assertRaises(ValueError):
            idf(5, 4, "classic")


class ProductTests(unittest.TestCase):
    def test_product(self) -> None:
        self.assertAlmostEqual(tfidf(2 / 14, math.log(4)), (2 / 14) * math.log(4))


if __name__ == "__main__":
    unittest.main()
