"""Readers for the frozen 2012 Gutenberg snapshot."""

from __future__ import annotations

from math import log
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tests.support import GUTENBERG, OUTPUT
from tfidfkit.similarity import cosine, query_vector
from tfidfkit.tables import load_committed, parse_idf_value
from tfidfkit.tokenize import tokenize_document
from tfidfkit.weights import run_pipeline


class ParseIdfValueTests(unittest.TestCase):
    def test_plain_float(self) -> None:
        value, dirty = parse_idf_value("2.89037175789616")
        self.assertFalse(dirty)
        self.assertAlmostEqual(value, log(18))

    def test_trailing_junk_from_the_snapshot(self) -> None:
        value, dirty = parse_idf_value("2.89037175789616y")
        self.assertTrue(dirty)
        self.assertAlmostEqual(value, log(18))


class CommittedSnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tables = load_committed(OUTPUT)

    def test_corpus_shape(self) -> None:
        self.assertEqual(len(self.tables.tfidf), 18)
        self.assertEqual(len(self.tables.idf), 57368)
        self.assertEqual(len(self.tables.df), 57368)

    def test_idf_matches_ln_18_over_df(self) -> None:
        mismatches = 0
        for token, (df, _names) in self.tables.df.items():
            expected = log(18 / df)
            if abs(expected - self.tables.idf[token]) > 1e-9:
                mismatches += 1
        self.assertEqual(mismatches, 0)

    def test_zero_idf_count(self) -> None:
        zeros = [token for token, value in self.tables.idf.items() if value == 0.0]
        self.assertEqual(len(zeros), 221)
        self.assertIn("the", zeros)
        self.assertIn("world", zeros)
        self.assertNotIn("alice", zeros)

    def test_dirty_thatyou_row(self) -> None:
        self.assertEqual(self.tables.dirty_idf, ("thatyou",))
        self.assertAlmostEqual(self.tables.idf["thatyou"], log(18))

    def test_alice_postings(self) -> None:
        df, names = self.tables.df["alice"]
        self.assertEqual(df, 3)
        self.assertCountEqual(
            names,
            (
                "carroll-alice.txt",
                "chesterton-thursday.txt",
                "edgeworth-parents.txt",
            ),
        )

    def test_alice_outranks_dormouse(self) -> None:
        weights = self.tables.tfidf["carroll-alice.txt"]
        self.assertGreater(weights["alice"], weights["dormouse"])
        self.assertAlmostEqual(weights["dormouse"], weights["duchess"])
        self.assertEqual(weights["the"], 0.0)

    def test_product_identity_on_alice(self) -> None:
        token = "alice"
        tf = self.tables.tf["carroll-alice.txt"][token]
        idf = self.tables.idf[token]
        tfidf = self.tables.tfidf["carroll-alice.txt"][token]
        self.assertAlmostEqual(tf * idf, tfidf, places=12)

    def test_moby_dick_query(self) -> None:
        query = query_vector("white whale ahab pequod", self.tables.idf)
        ranked = sorted(
            (
                (name, cosine(query, weights))
                for name, weights in self.tables.tfidf.items()
            ),
            key=lambda item: item[1],
            reverse=True,
        )
        self.assertEqual(ranked[0][0], "melville-moby_dick.txt")
        self.assertGreater(ranked[0][1], 0.4)
        self.assertGreater(ranked[0][1], ranked[1][1] * 10)

    def test_compat_tokenizer_matches_alice_denominator(self) -> None:
        stats = tokenize_document(
            GUTENBERG / "carroll-alice.txt", count_empty_tokens=True
        )
        alice_tf = self.tables.tf["carroll-alice.txt"]["alice"]
        inferred_n = stats.counts["alice"] / alice_tf
        self.assertAlmostEqual(stats.token_count, inferred_n, places=6)

    def test_compat_pipeline_matches_committed_alice_tf(self) -> None:
        result = run_pipeline(GUTENBERG, count_empty_tokens=True)
        snap = self.tables.tf["carroll-alice.txt"]
        recomputed = result.tf["carroll-alice.txt"]
        self.assertEqual(set(recomputed), set(snap))
        for token, value in snap.items():
            self.assertAlmostEqual(recomputed[token], value, places=12)


if __name__ == "__main__":
    unittest.main()
