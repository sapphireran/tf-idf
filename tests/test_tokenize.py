"""Tokenizer tests for the personal TF-IDF lab."""

from __future__ import annotations

import unittest

from tfidf.tokenize import perl_legacy_tokens, simple_tokens, tokenize


class SimpleTokenizerTests(unittest.TestCase):
    def test_lowercases_and_keeps_alnum_runs(self) -> None:
        self.assertEqual(
            simple_tokens("The Cat sat on the mat."),
            ["the", "cat", "sat", "on", "the", "mat"],
        )

    def test_splits_hyphens_and_apostrophes(self) -> None:
        self.assertEqual(simple_tokens("rabbit-hole"), ["rabbit", "hole"])
        self.assertEqual(simple_tokens("don't"), ["don", "t"])
        self.assertEqual(simple_tokens("Alice's"), ["alice", "s"])

    def test_keeps_years(self) -> None:
        self.assertEqual(simple_tokens("[Emma 1816]"), ["emma", "1816"])

    def test_empty(self) -> None:
        self.assertEqual(simple_tokens(""), [])
        tokens, length = tokenize("", tokenizer="simple")
        self.assertEqual(tokens, [])
        self.assertEqual(length, 0)


class PerlLegacyTokenizerTests(unittest.TestCase):
    def test_smashes_apostrophes_and_hyphens(self) -> None:
        tokens, length = perl_legacy_tokens("Don't climb the rabbit-hole.")
        self.assertEqual(tokens, ["dont", "climb", "the", "rabbithole"])
        self.assertEqual(length, 4)

    def test_counts_empty_split_pieces_in_length(self) -> None:
        tokens, length = perl_legacy_tokens("Hello.\n...")
        self.assertEqual(tokens, ["hello"])
        # "..." strips to "" and split(" ") yields one empty piece.
        self.assertEqual(length, 2)

    def test_title_years_survive(self) -> None:
        tokens, _ = perl_legacy_tokens("[Alice's Adventures in Wonderland 1865]")
        self.assertIn("1865", tokens)
        self.assertIn("alices", tokens)


class DispatchTests(unittest.TestCase):
    def test_unknown_tokenizer(self) -> None:
        with self.assertRaises(ValueError):
            tokenize("hello", tokenizer="unicode")


if __name__ == "__main__":
    unittest.main()
