"""Sanity checks against the checked-in Perl snapshot under output/."""

from __future__ import annotations

import math
import unittest

from support import GUTENBERG_TFIDF, ROOT

from tfidf_lib import read_score_tsv, reconstruct_df, top_terms

N = 18


class GutenbergSnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.idf = read_score_tsv(ROOT / "output" / "idf.txt")

    def test_n_is_eighteen_from_ceiling_idf(self) -> None:
        # One-document terms sit at ln(18).
        self.assertAlmostEqual(max(self.idf.values()), math.log(N), places=10)

    def test_collection_wide_a_has_idf_zero(self) -> None:
        self.assertEqual(self.idf["a"], 0)

    def test_reconstructed_df_for_famous_terms(self) -> None:
        expected = {
            "alice": 3,
            "ahab": 2,
            "emma": 2,
            "whale": 6,
            "hamlet": 6,
        }
        for term, df in expected.items():
            recovered = reconstruct_df(N, self.idf[term])
            self.assertAlmostEqual(recovered, df, places=8, msg=term)

    def test_alice_ranks_first_in_carroll(self) -> None:
        scores = read_score_tsv(GUTENBERG_TFIDF / "carroll-alice.txt")
        self.assertEqual(top_terms(scores, 1)[0][0], "alice")

    def test_moby_dick_opens_with_whale_and_ahab(self) -> None:
        scores = read_score_tsv(GUTENBERG_TFIDF / "melville-moby_dick.txt")
        head = [term for term, _ in top_terms(scores, 5)]
        self.assertEqual(head[0], "whale")
        self.assertEqual(head[1], "ahab")
        self.assertIn("queequeg", head)

    def test_emma_is_led_by_character_names(self) -> None:
        scores = read_score_tsv(GUTENBERG_TFIDF / "austen-emma.txt")
        head = [term for term, _ in top_terms(scores, 5)]
        self.assertEqual(head[0], "emma")
        self.assertIn("harriet", head)
        self.assertIn("knightley", head)

    def test_hamlet_speech_prefix_outranks_the_title_name(self) -> None:
        scores = read_score_tsv(GUTENBERG_TFIDF / "shakespeare-hamlet.txt")
        ranked = top_terms(scores, 20)
        terms = [term for term, _ in ranked]
        self.assertEqual(terms[0], "ham")
        if "hamlet" in scores:
            ham = dict(ranked).get("ham", scores["ham"])
            self.assertGreater(ham, scores["hamlet"])


if __name__ == "__main__":
    unittest.main()
