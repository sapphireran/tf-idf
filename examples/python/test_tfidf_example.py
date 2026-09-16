#!/usr/bin/env python3
"""Identities for the three-document tiny corpus and for tokenization."""

from __future__ import annotations

import math
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import tfidf_example  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[2]
TINY_DOCS = REPO_ROOT / "examples" / "tiny-corpus" / "docs"
EXPECTED = REPO_ROOT / "examples" / "tiny-corpus" / "expected"
LN3 = math.log(3)
LN3_OVER_6 = LN3 / 6


class IterDocumentsTests(unittest.TestCase):
    def test_skips_markdown_readme(self) -> None:
        excerpt_dir = REPO_ROOT / "examples" / "excerpts"
        names = [p.name for p in tfidf_example.iter_documents(excerpt_dir)]
        self.assertEqual(
            names,
            ["alice-opening.txt", "macbeth-witches.txt", "moby-cetology.txt"],
        )
        self.assertNotIn("README.md", names)


class TokenizeTests(unittest.TestCase):
    def test_alices_loses_apostrophe(self) -> None:
        self.assertEqual(
            tfidf_example.tokenize_line("Alice's Adventures"),
            ["alices", "adventures"],
        )

    def test_im_late(self) -> None:
        self.assertEqual(tfidf_example.tokenize_line("I'm late!"), ["im", "late"])

    def test_digits_kept(self) -> None:
        self.assertEqual(tfidf_example.tokenize_line("1865"), ["1865"])

    def test_empty_punctuation_line(self) -> None:
        self.assertEqual(tfidf_example.tokenize_line("... --"), [])

    def test_file_matches_line_join(self) -> None:
        text = "The Cat\nSat on the Mat!"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.txt"
            path.write_text(text, encoding="utf-8")
            self.assertEqual(
                tfidf_example.tokenize_file(path),
                ["the", "cat", "sat", "on", "the", "mat"],
            )


class TinyCorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = tfidf_example.compute(TINY_DOCS)

    def test_n_is_three(self) -> None:
        self.assertEqual(self.result["n"], 3)

    def test_lengths(self) -> None:
        self.assertEqual(self.result["lengths"]["cats.txt"], 6)
        self.assertEqual(self.result["lengths"]["dogs.txt"], 6)
        self.assertEqual(self.result["lengths"]["birds.txt"], 6)

    def test_vocabulary(self) -> None:
        self.assertEqual(
            set(self.result["idf"]),
            {"a", "bird", "cat", "dog", "log", "mat", "nest", "on", "sat", "the"},
        )

    def test_df(self) -> None:
        df = {term: len(docs) for term, docs in self.result["df_docs"].items()}
        self.assertEqual(df["the"], 3)
        self.assertEqual(df["sat"], 3)
        self.assertEqual(df["on"], 3)
        self.assertEqual(df["cat"], 1)
        self.assertEqual(df["a"], 1)

    def test_idf_zero_for_shared_words(self) -> None:
        for term in ("the", "sat", "on"):
            self.assertEqual(self.result["idf"][term], 0.0)

    def test_idf_ln3_for_unique_words(self) -> None:
        for term in ("cat", "mat", "dog", "log", "a", "bird", "nest"):
            self.assertAlmostEqual(self.result["idf"][term], LN3)

    def test_tf_the_in_cats(self) -> None:
        self.assertAlmostEqual(self.result["tf"]["cats.txt"]["the"], 2 / 6)

    def test_tfidf_cat(self) -> None:
        self.assertAlmostEqual(self.result["tfidf"]["cats.txt"]["cat"], LN3_OVER_6)
        self.assertAlmostEqual(self.result["tfidf"]["cats.txt"]["mat"], LN3_OVER_6)
        self.assertEqual(self.result["tfidf"]["cats.txt"]["the"], 0.0)

    def test_tfidf_birds_article_is_distinctive_here(self) -> None:
        # In the Gutenberg collection, "a" has IDF 0. In this shelf it does not.
        self.assertAlmostEqual(self.result["tfidf"]["birds.txt"]["a"], LN3_OVER_6)
        self.assertAlmostEqual(self.result["tfidf"]["birds.txt"]["bird"], LN3_OVER_6)

    def test_expected_idf_file(self) -> None:
        written = (EXPECTED / "idf.txt").read_text(encoding="utf-8")
        self.assertIn("cat\t1.0986122886681098\n", written)
        self.assertIn("the\t0.0\n", written)

    def test_write_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            tfidf_example.write_tables(self.result, out)
            idf_again = (out / "idf.txt").read_text(encoding="utf-8")
            expected = (EXPECTED / "idf.txt").read_text(encoding="utf-8")
            self.assertEqual(idf_again, expected)
            self.assertEqual(
                (out / "tfidf" / "cats.txt").read_text(encoding="utf-8"),
                (EXPECTED / "tfidf" / "cats.txt").read_text(encoding="utf-8"),
            )


class ExcerptCollectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = tfidf_example.compute(REPO_ROOT / "examples" / "excerpts")

    def test_n_is_three_txt_files(self) -> None:
        self.assertEqual(self.result["n"], 3)

    def test_alice_outranks_the(self) -> None:
        weights = self.result["tfidf"]["alice-opening.txt"]
        self.assertGreater(weights["alice"], weights.get("the", 0.0))
        self.assertGreater(weights["she"], weights["alice"])

    def test_whale_leads_moby_excerpt(self) -> None:
        weights = self.result["tfidf"]["moby-cetology.txt"]
        top = max(weights, key=weights.get)
        self.assertEqual(top, "whale")


class AliceGutenbergIdentityTests(unittest.TestCase):
    """Spot-check the committed Perl tables against the documented product."""

    def test_alice_tf_times_idf(self) -> None:
        tf_row = None
        idf_row = None
        product_row = None
        tf_path = REPO_ROOT / "output" / "tf" / "carroll-alice.txt"
        idf_path = REPO_ROOT / "output" / "idf.txt"
        tfidf_path = REPO_ROOT / "output" / "tfidf" / "carroll-alice.txt"
        for line in tf_path.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("alice\t"):
                tf_row = float(line.split("\t")[1])
                break
        for line in idf_path.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("alice\t"):
                idf_row = float(line.split("\t")[1])
                break
        for line in tfidf_path.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("alice\t"):
                product_row = float(line.split("\t")[1])
                break
        self.assertIsNotNone(tf_row)
        self.assertIsNotNone(idf_row)
        self.assertIsNotNone(product_row)
        self.assertAlmostEqual(idf_row, math.log(18 / 3), places=12)
        self.assertAlmostEqual(tf_row * idf_row, product_row, places=12)


if __name__ == "__main__":
    unittest.main()
