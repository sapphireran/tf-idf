"""Checked-in expected TSVs must match a fresh teaching-pipeline run."""

from __future__ import annotations

import unittest

from support import MICRO, ROOT, TINY

from tfidf_lib import read_score_tsv, score_collection, top_terms

MICRO_EXPECTED = ROOT / "examples" / "micro-corpus-expected"
TINY_EXPECTED = ROOT / "examples" / "tiny-corpus-expected"


class ExpectedOutputTests(unittest.TestCase):
    def test_micro_idf_matches_checked_in_file(self) -> None:
        fresh = score_collection(MICRO)
        stored = read_score_tsv(MICRO_EXPECTED / "idf.txt", skip_bad=False)
        self.assertEqual(set(fresh.idf), set(stored))
        for term, value in fresh.idf.items():
            self.assertAlmostEqual(value, stored[term], places=12, msg=term)

    def test_micro_tfidf_matches_checked_in_files(self) -> None:
        fresh = score_collection(MICRO)
        for document in fresh.documents:
            stored = read_score_tsv(
                MICRO_EXPECTED / "tfidf" / document.name, skip_bad=False
            )
            self.assertEqual(set(document.tfidf), set(stored))
            for term, value in document.tfidf.items():
                self.assertAlmostEqual(value, stored[term], places=12, msg=term)

    def test_tiny_top_terms_match_sample_ranking(self) -> None:
        fresh = score_collection(TINY)
        expected_heads = {
            "cats.txt": ["purr", "cat", "cats", "sofa", "whiskers", "yarn"],
            "dogs.txt": ["bark", "dog", "dogs", "ears", "garden", "yard"],
            "baking.txt": ["dough", "bread", "flour", "ovens"],
        }
        for name, head in expected_heads.items():
            document = next(doc for doc in fresh.documents if doc.name == name)
            ranked = [term for term, _ in top_terms(document.tfidf, len(head))]
            self.assertEqual(ranked, head)
            stored = read_score_tsv(TINY_EXPECTED / "tfidf" / name)
            stored_head = [term for term, _ in top_terms(stored, len(head))]
            self.assertEqual(stored_head, head)
