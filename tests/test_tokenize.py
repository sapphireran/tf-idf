"""Tokenizer behavior documented in docs/tokenization.md."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tfidf_toy.tokenize import tokenize, tokenize_line


class TokenizeLineTests(unittest.TestCase):
    def test_lowercases_and_strips_punctuation(self) -> None:
        tokens, length = tokenize_line("Oh dear!")
        self.assertEqual(tokens, ["oh", "dear"])
        self.assertEqual(length, 2)

    def test_possessive_loses_apostrophe(self) -> None:
        tokens, _ = tokenize_line("Alice's")
        self.assertEqual(tokens, ["alices"])

    def test_hyphen_is_deleted_not_split(self) -> None:
        tokens, _ = tokenize_line("rabbit-hole")
        self.assertEqual(tokens, ["rabbithole"])

    def test_digits_are_kept(self) -> None:
        tokens, _ = tokenize_line("CHAPTER I. 1865")
        self.assertEqual(tokens, ["chapter", "i", "1865"])

    def test_empty_and_punctuation_only_lines(self) -> None:
        self.assertEqual(tokenize_line(""), ([], 0))
        self.assertEqual(tokenize_line("   "), ([], 0))
        self.assertEqual(tokenize_line("!!!"), ([], 0))

    def test_quotes_and_emdash_like_ascii(self) -> None:
        tokens, _ = tokenize_line('"Hello?" -- said Alice.')
        self.assertEqual(tokens, ["hello", "said", "alice"])


class PerlLengthQuirkTests(unittest.TestCase):
    def test_default_ignores_leading_space_in_length(self) -> None:
        tokens, length = tokenize_line("  hello world  ")
        self.assertEqual(tokens, ["hello", "world"])
        self.assertEqual(length, 2)

    def test_match_perl_length_counts_leading_empty_field(self) -> None:
        tokens, length = tokenize_line("  hello world  ", match_perl_length=True)
        self.assertEqual(tokens, ["hello", "world"])
        # Perl split(/ +/, " hello world ") -> ('', 'hello', 'world'); trailing empty dropped.
        self.assertEqual(length, 3)

    def test_match_perl_length_without_leading_space_matches_token_count(self) -> None:
        tokens, length = tokenize_line("hello world", match_perl_length=True)
        self.assertEqual(tokens, ["hello", "world"])
        self.assertEqual(length, 2)


class TokenizeDocumentTests(unittest.TestCase):
    def test_worked_example_alice_line(self) -> None:
        text = (ROOT / "examples" / "tiny_corpus" / "alice.txt").read_text()
        tokens, length = tokenize(text)
        self.assertEqual(
            tokens, ["alice", "chased", "the", "rabbit", "the", "rabbit", "was", "late"]
        )
        self.assertEqual(length, 8)

    def test_worked_example_whale_line(self) -> None:
        text = (ROOT / "examples" / "tiny_corpus" / "whale.txt").read_text()
        tokens, length = tokenize(text)
        self.assertEqual(
            tokens,
            ["the", "whale", "struck", "the", "ship", "the", "ship", "was", "late"],
        )
        self.assertEqual(length, 9)

    def test_multiline_sums_length(self) -> None:
        tokens, length = tokenize("Hello world.\nHello!")
        self.assertEqual(tokens, ["hello", "world", "hello"])
        self.assertEqual(length, 3)


if __name__ == "__main__":
    unittest.main()
