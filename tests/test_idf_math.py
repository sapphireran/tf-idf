"""Boundary cases for the IDF function itself."""

from __future__ import annotations

import math
import unittest

from support import ROOT  # noqa: F401

from tfidf_lib import inverse_document_frequency, reconstruct_df, top_terms


class IdfMathTests(unittest.TestCase):
    def test_collection_wide_term_is_zero(self) -> None:
        self.assertEqual(inverse_document_frequency(18, 18), 0.0)

    def test_singleton_term_is_ln_n(self) -> None:
        self.assertEqual(inverse_document_frequency(18, 1), math.log(18))

    def test_rejects_zero_df(self) -> None:
        with self.assertRaises(ValueError):
            inverse_document_frequency(18, 0)

    def test_rejects_df_above_n(self) -> None:
        with self.assertRaises(ValueError):
            inverse_document_frequency(18, 19)

    def test_reconstruct_is_inverse(self) -> None:
        for n, df in ((3, 1), (3, 2), (18, 6), (18, 18)):
            idf = inverse_document_frequency(n, df)
            self.assertAlmostEqual(reconstruct_df(n, idf), df)


class TopTermsTests(unittest.TestCase):
    def test_tie_breaks_are_lexicographic(self) -> None:
        ranked = top_terms({"mat": 1.0, "cat": 1.0, "the": 0.5}, 3)
        self.assertEqual([term for term, _ in ranked], ["cat", "mat", "the"])

    def test_limit_zero(self) -> None:
        self.assertEqual(top_terms({"cat": 1.0}, 0), [])

    def test_rejects_negative_limit(self) -> None:
        with self.assertRaises(ValueError):
            top_terms({"cat": 1.0}, -1)
