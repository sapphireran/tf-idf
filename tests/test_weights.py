"""Hand-calculated classic weights on a three-line corpus."""

from __future__ import annotations

import math
import unittest

from querydesk.tokenize import count_text
from querydesk.weights import document_frequencies, idf_map, idf_value, normalized_tf, tfidf_map


class IdfVariantTests(unittest.TestCase):
    def test_classic_hapax_and_universal(self) -> None:
        self.assertAlmostEqual(idf_value(18, 1, "classic"), math.log(18))
        self.assertEqual(idf_value(18, 18, "classic"), 0.0)

    def test_smooth_universal_is_negative(self) -> None:
        self.assertLess(idf_value(18, 18, "smooth"), 0.0)

    def test_sklearnish_never_zero(self) -> None:
        self.assertGreater(idf_value(18, 18, "sklearnish"), 0.0)


class HandExampleTests(unittest.TestCase):
    """docs/05 three one-line documents."""

    def setUp(self) -> None:
        raw = {
            "alpha.txt": count_text("cairn cairn ice"),
            "beta.txt": count_text("chase type"),
            "gamma.txt": count_text("cairn type"),
        }
        self.raw = raw
        self.df = document_frequencies(counts for counts, _ in raw.values())
        self.idf = idf_map(self.df, 3, "classic")

    def test_df(self) -> None:
        self.assertEqual(self.df, {"cairn": 2, "ice": 1, "chase": 1, "type": 2})

    def test_idf(self) -> None:
        self.assertAlmostEqual(self.idf["ice"], math.log(3))
        self.assertAlmostEqual(self.idf["cairn"], math.log(3 / 2))

    def test_alpha_tfidf(self) -> None:
        counts, word_count = self.raw["alpha.txt"]
        self.assertEqual(word_count, 3)
        tf = normalized_tf(counts, word_count)
        tfidf = tfidf_map(tf, self.idf)
        self.assertAlmostEqual(tf["cairn"], 2 / 3)
        self.assertAlmostEqual(tfidf["cairn"], (2 / 3) * math.log(3 / 2))
        self.assertAlmostEqual(tfidf["ice"], (1 / 3) * math.log(3))
