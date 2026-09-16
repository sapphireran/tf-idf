"""Tokenizer tests: punctuation deletion, case folding, empty fields."""

from __future__ import annotations

import unittest

from support import ROOT  # noqa: F401  — installs examples/python on sys.path

from tfidf_lib import tokenize_line, tokenize_text, count_tokens


class TokenizeLineTests(unittest.TestCase):
    def test_lowercases_ascii(self) -> None:
        self.assertEqual(tokenize_line("Cats PURR"), ["cats", "purr"])

    def test_strips_apostrophes_without_splitting(self) -> None:
        self.assertEqual(tokenize_line("Alice's adventures"), ["alices", "adventures"])
        self.assertEqual(tokenize_line("o'er the vales"), ["oer", "the", "vales"])
        self.assertEqual(tokenize_line("pass'd"), ["passd"])

    def test_strips_hyphens_without_splitting(self) -> None:
        self.assertEqual(tokenize_line("Moby-Dick"), ["mobydick"])
        self.assertEqual(tokenize_line("well-known sailor"), ["wellknown", "sailor"])

    def test_strips_folio_punctuation(self) -> None:
        self.assertEqual(tokenize_line("Ham."), ["ham"])
        self.assertEqual(tokenize_line("Haue I"), ["haue", "i"])

    def test_keeps_digits(self) -> None:
        self.assertEqual(tokenize_line("year 1865"), ["year", "1865"])

    def test_empty_and_whitespace_lines(self) -> None:
        self.assertEqual(tokenize_line(""), [])
        self.assertEqual(tokenize_line("   "), [])

    def test_keep_empty_counts_leading_space_fields(self) -> None:
        tokens = tokenize_line("  hello  ", keep_empty=True)
        self.assertEqual(tokens, ["", "hello", ""])

    def test_default_drops_empty_fields(self) -> None:
        self.assertEqual(tokenize_line("  hello  "), ["hello"])


class TokenizeTextTests(unittest.TestCase):
    def test_line_breaks_are_boundaries_not_characters(self) -> None:
        text = "the cat sat\non the mat"
        self.assertEqual(
            tokenize_text(text),
            ["the", "cat", "sat", "on", "the", "mat"],
        )


class CountTokensTests(unittest.TestCase):
    def test_empty_strings_are_never_terms(self) -> None:
        counts, words = count_tokens(["", "cat", ""], count_empty=True)
        self.assertEqual(dict(counts), {"cat": 1})
        self.assertEqual(words, 3)

    def test_empty_strings_ignored_by_default_denominator(self) -> None:
        counts, words = count_tokens(["", "cat", ""], count_empty=False)
        self.assertEqual(dict(counts), {"cat": 1})
        self.assertEqual(words, 1)


if __name__ == "__main__":
    unittest.main()
