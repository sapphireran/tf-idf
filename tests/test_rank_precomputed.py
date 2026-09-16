#!/usr/bin/env python3
"""Tests for scripts/rank_precomputed_tfidf.py against frozen Gutenberg tables."""

from __future__ import annotations

import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import rank_precomputed_tfidf as ranker  # noqa: E402


class RankPrecomputedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.alice = ranker.load_scores(ROOT / "output" / "tfidf" / "carroll-alice.txt")
        cls.moby = ranker.load_scores(ROOT / "output" / "tfidf" / "melville-moby_dick.txt")
        cls.buster = ranker.load_scores(
            ROOT / "output" / "tfidf" / "burgess-busterbrown.txt"
        )

    def test_alice_is_the_fingerprint_of_alice(self) -> None:
        self.assertGreaterEqual(len(self.alice), 8)
        self.assertEqual(self.alice[0][0], "alice")
        self.assertAlmostEqual(self.alice[0][1], 0.025957, places=6)

    def test_moby_dick_leads_with_whale_then_ahab(self) -> None:
        self.assertEqual(self.moby[0][0], "whale")
        self.assertEqual(self.moby[1][0], "ahab")

    def test_buster_outscores_alice_head_term(self) -> None:
        self.assertEqual(self.buster[0][0], "buster")
        self.assertGreater(self.buster[0][1], self.alice[0][1])

    def test_skips_non_float_rows(self) -> None:
        bogus = ROOT / "tests" / "_tmp_bogus.tsv"
        try:
            bogus.write_text("ok\t1.5\nbad\t1.5y\nalso\t2.0\n", encoding="utf-8")
            rows = ranker.load_scores(bogus)
            self.assertEqual(rows, [("also", 2.0), ("ok", 1.5)])
        finally:
            if bogus.exists():
                bogus.unlink()


if __name__ == "__main__":
    unittest.main()
