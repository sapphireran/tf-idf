"""Tests for the personal tf-idf reference implementation."""

from __future__ import annotations

from math import isclose, log
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON_DIR = ROOT / "examples" / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from tfidf_lab import (  # noqa: E402
    Document,
    build_index,
    build_worked_example,
    cosine_similarity,
    load_documents,
    natural_idf,
    tf_proportion,
    tokenize,
)


class TokenizeTests(unittest.TestCase):
    def test_lowercases_and_drops_punctuation(self) -> None:
        self.assertEqual(
            tokenize("Hello, Alice's cat!"),
            ["hello", "alices", "cat"],
        )

    def test_collapses_whitespace_and_drops_empties(self) -> None:
        self.assertEqual(tokenize("  one\n\ttwo  "), ["one", "two"])

    def test_keeps_digits(self) -> None:
        self.assertEqual(tokenize("Room 221B"), ["room", "221b"])

    def test_perl_empty_count_keeps_leading_empty(self) -> None:
        tokens = tokenize(" leading", count_empty_like_perl=True)
        self.assertEqual(tokens[0], "")
        self.assertIn("leading", tokens)


class FormulaTests(unittest.TestCase):
    def test_idf_matches_natural_log(self) -> None:
        self.assertTrue(isclose(natural_idf(18, 1), log(18)))
        self.assertTrue(isclose(natural_idf(3, 2), log(1.5)))

    def test_idf_rejects_zero_df(self) -> None:
        with self.assertRaises(ValueError):
            natural_idf(3, 0)

    def test_tf_is_a_proportion(self) -> None:
        self.assertEqual(tf_proportion(1, 4), 0.25)

    def test_cosine_of_identical_vectors_is_one(self) -> None:
        vector = {"cats": 0.3, "mats": 0.1}
        self.assertTrue(isclose(cosine_similarity(vector, vector), 1.0))

    def test_cosine_of_orthogonal_vectors_is_zero(self) -> None:
        self.assertEqual(
            cosine_similarity({"cats": 1.0}, {"dogs": 1.0}),
            0.0,
        )


class WorkedExampleTests(unittest.TestCase):
    def test_tokens_and_lengths(self) -> None:
        example = build_worked_example()
        by_name = {doc.name: doc for doc in example.documents}
        self.assertEqual(by_name["mats.txt"].tokens, ["cats", "sit", "on", "mats"])
        self.assertEqual(by_name["logs.txt"].tokens, ["dogs", "sit", "on", "logs"])
        self.assertEqual(by_name["chase.txt"].tokens, ["cats", "chase", "dogs"])

    def test_document_frequencies(self) -> None:
        stats = build_worked_example().index.stats
        self.assertEqual(stats["cats"].df, 2)
        self.assertEqual(stats["mats"].df, 1)
        self.assertEqual(stats["chase"].df, 1)
        self.assertEqual(stats["sit"].df, 2)

    def test_hand_calculated_tfidf_for_mats(self) -> None:
        example = build_worked_example()
        row = next(
            item
            for item in example.rows
            if item.document == "mats.txt" and item.term == "mats"
        )
        self.assertEqual(row.count, 1)
        self.assertEqual(row.length, 4)
        self.assertTrue(isclose(row.tf, 0.25))
        self.assertEqual(row.df, 1)
        self.assertTrue(isclose(row.idf, log(3)))
        self.assertTrue(isclose(row.tfidf, 0.25 * log(3)))

    def test_shared_word_has_lower_idf_than_unique_word(self) -> None:
        stats = build_worked_example().index.stats
        self.assertLess(stats["cats"].idf, stats["mats"].idf)


class TinyCorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        docs_dir = ROOT / "examples" / "tiny_corpus" / "docs"
        cls.docs = load_documents(docs_dir)
        cls.index = build_index(cls.docs)

    def test_five_original_documents(self) -> None:
        names = {doc.name for doc in self.docs}
        self.assertEqual(
            names,
            {
                "harbor-cats.txt",
                "trail-dogs.txt",
                "sourdough-baking.txt",
                "winter-constellations.txt",
                "kitchen-garden.txt",
            },
        )

    def test_cat_document_prefers_feline_vocabulary(self) -> None:
        top = [term for term, _ in self.index.scored["harbor-cats.txt"].top_terms(8)]
        self.assertTrue({"cats", "tabby", "harbor", "feline"} & set(top))
        self.assertNotIn("telescope", top)
        self.assertNotIn("sourdough", top)

    def test_garden_document_leads_with_garden(self) -> None:
        top = [
            term
            for term, _
            in self.index.scored["kitchen-garden.txt"].top_terms(5)
        ]
        self.assertEqual(top[0], "garden")

    def test_dog_document_prefers_canine_vocabulary(self) -> None:
        top = [term for term, _ in self.index.scored["trail-dogs.txt"].top_terms(8)]
        self.assertTrue({"dogs", "leash", "trail"} & set(top))

    def test_baking_document_prefers_kitchen_vocabulary(self) -> None:
        top = [
            term
            for term, _
            in self.index.scored["sourdough-baking.txt"].top_terms(8)
        ]
        self.assertTrue({"starter", "crust", "dough", "baking"} & set(top))

    def test_astronomy_and_baking_are_less_similar_than_garden_and_baking(self) -> None:
        baking_garden = self.index.cosine(
            "sourdough-baking.txt", "kitchen-garden.txt"
        )
        baking_stars = self.index.cosine(
            "sourdough-baking.txt", "winter-constellations.txt"
        )
        self.assertGreater(baking_garden, baking_stars)

    def test_expected_tables_match_live_scores(self) -> None:
        expected_dir = ROOT / "examples" / "tiny_corpus" / "expected"
        if not (expected_dir / "idf.txt").exists():
            self.skipTest("expected tables have not been generated yet")
        from tfidf_lab import read_term_weights

        live = self.index.stats
        committed = read_term_weights(expected_dir / "idf.txt")
        self.assertEqual(set(committed), set(live))
        for term, value in committed.items():
            self.assertTrue(isclose(value, live[term].idf, rel_tol=1e-9))


class IndexVariantTests(unittest.TestCase):
    def test_log_tf_changes_scores_but_not_vocabulary(self) -> None:
        docs = [
            Document.from_text("a.txt", "cats cats mats"),
            Document.from_text("b.txt", "dogs mats"),
        ]
        repo = build_index(docs, variant="repo")
        log_tf = build_index(docs, variant="log_tf")
        self.assertEqual(repo.vocabulary(), log_tf.vocabulary())
        self.assertNotEqual(
            repo.scored["a.txt"].tf["cats"],
            log_tf.scored["a.txt"].tf["cats"],
        )


if __name__ == "__main__":
    unittest.main()
