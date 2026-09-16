"""Sanity checks against the committed Perl output/ and a live Gutenberg run."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tfidf_toy.model import TfIdfIndex, load_term_table, rank_overlap

LN18 = math.log(18)


class CommittedPerlOutputTests(unittest.TestCase):
    def test_alice_top_terms_are_character_names(self) -> None:
        table = load_term_table(ROOT / "output" / "tfidf" / "carroll-alice.txt")
        ranked = [term for term, _ in sorted(table.items(), key=lambda kv: (-kv[1], kv[0]))]
        self.assertEqual(ranked[0], "alice")
        for expected in ("gryphon", "duchess", "dormouse", "hatter"):
            self.assertIn(expected, ranked[:8], ranked[:12])

    def test_collection_wide_words_are_zero_in_alice(self) -> None:
        table = load_term_table(ROOT / "output" / "tfidf" / "carroll-alice.txt")
        for glue in ("a", "the", "and", "of", "about"):
            self.assertIn(glue, table)
            self.assertEqual(table[glue], 0.0)

    def test_hapax_document_idf_is_ln18(self) -> None:
        idf = load_term_table(ROOT / "output" / "idf.txt")
        # gryphon appears in Alice *and* Paradise Lost, so its idf is ln(18/2).
        self.assertAlmostEqual(idf["gryphon"], math.log(18 / 2), places=10)
        self.assertAlmostEqual(idf["dormouse"], LN18, places=10)
        self.assertAlmostEqual(idf["buster"], LN18, places=10)
        self.assertEqual(idf["the"], 0.0)
        self.assertEqual(idf["and"], 0.0)
        # one smashed row in the historical dump: score plus leftover "y"
        self.assertAlmostEqual(idf["thatyou"], LN18, places=10)

    def test_moby_dick_top_term_is_the_whale(self) -> None:
        table = load_term_table(ROOT / "output" / "tfidf" / "melville-moby_dick.txt")
        top = max(table, key=table.get)
        self.assertEqual(top, "whale")


class LiveGutenbergIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.index = TfIdfIndex.from_directory(ROOT / "gutenberg", idf_mode="raw")

    def test_eighteen_books(self) -> None:
        self.assertEqual(self.index.n_docs, 18)
        self.assertEqual(len(self.index.documents), 18)

    def test_alice_still_ranks_first_on_a_fresh_index(self) -> None:
        doc = self.index.get("carroll-alice.txt")
        self.assertEqual(doc.top_terms(1)[0][0], "alice")
        self.assertGreater(doc.tfidf["gryphon"], doc.tfidf["the"])
        self.assertEqual(self.index.idf["the"], 0.0)

    def test_python_top30_overlaps_committed_perl_alice(self) -> None:
        python_table = self.index.get("carroll-alice.txt").tfidf
        perl_table = load_term_table(ROOT / "output" / "tfidf" / "carroll-alice.txt")
        overlap, _, _ = rank_overlap(python_table, perl_table, k=30)
        self.assertGreaterEqual(
            overlap,
            28,
            "tokenizer/idf rewrite drifted too far from the committed Perl run",
        )

    def test_austen_compare_surfaces_heroines(self) -> None:
        left, right = self.index.compare("austen-emma.txt", "austen-sense.txt", k=15)
        emma_terms = {row[0] for row in left}
        sense_terms = {row[0] for row in right}
        self.assertTrue(
            {"emma", "woodhouse", "harriet", "knightley"} & emma_terms,
            emma_terms,
        )
        self.assertTrue(
            {"elinor", "marianne", "dashwood", "willoughby"} & sense_terms,
            sense_terms,
        )


if __name__ == "__main__":
    unittest.main()
