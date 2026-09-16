"""Slow-ish sanity checks on the eighteen Gutenberg files.

These are still personal-lab tests: public-domain books, qualitative
winners I would be embarrassed to get wrong. The index is built once
per class.
"""

from __future__ import annotations

import unittest

from tfidf.index import CorpusIndex, resolve_corpus
from tfidf.rank import rank_query


class GutenbergSanityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.index = CorpusIndex.from_directory(
            resolve_corpus("gutenberg"),
            tokenizer="simple",
        )

    def test_shelf_size_and_bible_is_longest(self) -> None:
        self.assertEqual(self.index.n_docs, 18)
        stats = self.index.corpus_stats()
        self.assertEqual(stats[0][0], "bible-kjv.txt")
        self.assertEqual(stats[-1][0], "blake-poems.txt")

    def test_alice_is_the_top_term_in_alice(self) -> None:
        top = self.index.top_terms("carroll-alice.txt", k=1, alpha_only=True)
        self.assertEqual(top[0][0], "alice")

    def test_whale_is_the_top_term_in_moby_dick(self) -> None:
        top = self.index.top_terms("melville-moby_dick.txt", k=1, alpha_only=True)
        self.assertEqual(top[0][0], "whale")

    def test_sanity_queries_under_cosine(self) -> None:
        cases = (
            ("white whale ahab", "melville-moby_dick.txt"),
            ("alice rabbit queen", "carroll-alice.txt"),
            ("macbeth witches thane", "shakespeare-macbeth.txt"),
            ("emma woodhouse hartfield", "austen-emma.txt"),
            ("father brown flambeau", "chesterton-brown.txt"),
            ("hamlet ghost horatio", "shakespeare-hamlet.txt"),
            ("paradise satan eden", "milton-paradise.txt"),
        )
        for query, expected in cases:
            ranked = rank_query(query, self.index, scheme="cosine", k=1)
            self.assertEqual(ranked[0].name, expected, query)
            self.assertGreater(ranked[0].score, 0.0, query)

    def test_bm25_also_elects_moby_dick_for_white_whale(self) -> None:
        ranked = rank_query("white whale", self.index, scheme="bm25", k=1)
        self.assertEqual(ranked[0].name, "melville-moby_dick.txt")


if __name__ == "__main__":
    unittest.main()
