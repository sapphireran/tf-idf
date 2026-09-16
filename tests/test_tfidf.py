#!/usr/bin/env python3
"""Checks for the personal tf-idf examples (tiny corpus + tokenizer)."""

from __future__ import annotations

import json
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON_EXAMPLES = ROOT / "examples" / "python"
if str(PYTHON_EXAMPLES) not in sys.path:
    sys.path.insert(0, str(PYTHON_EXAMPLES))

import tfidf as tfidf_lib  # noqa: E402


class TokenizeTests(unittest.TestCase):
    def test_lowercase_and_punctuation(self) -> None:
        tokens = tfidf_lib.tokenize("Alice's Rabbit-Hole, 1865!")
        self.assertEqual(tokens, ["alices", "rabbithole", "1865"])

    def test_whitespace_collapse(self) -> None:
        tokens = tfidf_lib.tokenize("the   cat\tsat\non  the mat")
        self.assertEqual(tokens, ["the", "cat", "sat", "on", "the", "mat"])

    def test_faithful_perl_keeps_leading_empty(self) -> None:
        faithful = tfidf_lib.tokenize("  leading space", faithful_perl=True)
        clean = tfidf_lib.tokenize("  leading space", faithful_perl=False)
        self.assertEqual(faithful[0], "")
        self.assertEqual(clean[0], "leading")


class TinyCorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        expected_path = ROOT / "examples" / "tiny-corpus" / "expected.json"
        cls.expected = json.loads(expected_path.read_text(encoding="utf-8"))
        documents = tfidf_lib.load_directory(ROOT / "examples" / "tiny-corpus")
        cls.index = tfidf_lib.build_index(documents, idf_variant="raw")

    def test_document_count(self) -> None:
        self.assertEqual(self.index.N, 3)
        self.assertEqual({doc.name for doc in self.index.documents}, set(self.expected["tfidf"]))

    def test_idf_matches_hand_calculation(self) -> None:
        for term, value in self.expected["idf"].items():
            self.assertAlmostEqual(self.index.idf[term], value, delta=1e-12, msg=term)
        self.assertEqual(self.index.idf["the"], 0.0)
        self.assertAlmostEqual(self.index.idf["cat"], math.log(3), delta=1e-15)

    def test_tfidf_matches_hand_calculation(self) -> None:
        for name, terms in self.expected["tfidf"].items():
            document = self.index.document_by_name(name)
            got = self.index.tfidf(document)
            self.assertEqual(set(got), set(terms))
            for term, value in terms.items():
                self.assertAlmostEqual(got[term], value, delta=1e-12, msg=f"{name}:{term}")

    def test_universal_term_does_not_rank(self) -> None:
        cats = self.index.document_by_name("cats.txt")
        top_terms = [term for term, _score in self.index.ranked(cats, limit=2)]
        self.assertEqual(sorted(top_terms), ["cat", "mat"])
        self.assertNotIn("the", top_terms)

    def test_sklearn_idf_keeps_universal_term_nonzero(self) -> None:
        sklearn_index = tfidf_lib.build_index(self.index.documents, idf_variant="sklearn")
        self.assertGreater(sklearn_index.idf["the"], 0.0)
        cats = sklearn_index.document_by_name("cats.txt")
        self.assertGreater(sklearn_index.tfidf(cats)["the"], 0.0)

    def test_dump_payload_round_trips_n(self) -> None:
        payload = tfidf_lib.index_as_expected_payload(self.index)
        self.assertEqual(payload["N"], 3)
        self.assertIn("birds.txt", payload["tfidf"])


class ThemesCorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        documents = tfidf_lib.load_directory(ROOT / "examples" / "themes-corpus")
        cls.index = tfidf_lib.build_index(documents)

    def test_theme_words_lead_each_file(self) -> None:
        expected_leaders = {
            "bakery.txt": {"baker", "flour", "dough", "bakery", "cakes"},
            "observatory.txt": {"stars", "telescope", "astronomer", "observatory"},
            "concert.txt": {"violin", "melody", "violinist", "concert"},
        }
        for name, allowed in expected_leaders.items():
            document = self.index.document_by_name(name)
            top, _score = self.index.ranked(document, limit=1)[0]
            self.assertIn(top, allowed, msg=f"{name} top term {top!r}")

    def test_bakery_is_closest_to_itself(self) -> None:
        bakery = self.index.document_by_name("bakery.txt")
        bakery_vec = self.index.vector(bakery)
        scores = {
            document.name: tfidf_lib.cosine_similarity(bakery_vec, self.index.vector(document))
            for document in self.index.documents
        }
        self.assertAlmostEqual(scores["bakery.txt"], 1.0, delta=1e-12)
        self.assertGreater(scores["bakery.txt"], scores["observatory.txt"])
        self.assertGreater(scores["bakery.txt"], scores["concert.txt"])


class TopTermsReaderTests(unittest.TestCase):
    def test_alice_still_ranks_first_in_committed_output(self) -> None:
        sys.path.insert(0, str(PYTHON_EXAMPLES))
        import top_terms

        rows = top_terms.read_tfidf_table(ROOT / "output" / "tfidf" / "carroll-alice.txt")
        self.assertEqual(rows[0][0], "alice")
        self.assertGreater(rows[0][1], 0.02)


if __name__ == "__main__":
    unittest.main()
