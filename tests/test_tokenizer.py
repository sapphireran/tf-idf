"""Tokenizer behavior, including the Perl empty-token quirk."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tests.support import PYTHON_EXAMPLES  # noqa: F401  # installs tfidfkit path
from tfidfkit.tokenize import normalize_line, split_perl_spaces, tokenize_text


class NormalizeLineTests(unittest.TestCase):
    def test_lowercases_and_strips_punctuation(self) -> None:
        self.assertEqual(normalize_line("Alice's Rabbit-Hole!"), "alices rabbithole")

    def test_keeps_digits(self) -> None:
        self.assertEqual(normalize_line("[Carroll 1865]"), "carroll 1865")

    def test_collapses_whitespace(self) -> None:
        self.assertEqual(normalize_line("cats\t\tsit   on\nmats"), "cats sit on mats")

    def test_drops_apostrophes_like_the_perl_script(self) -> None:
        self.assertEqual(normalize_line("I'm don't"), "im dont")


class TokenizeTextTests(unittest.TestCase):
    def test_counts_simple_document(self) -> None:
        stats = tokenize_text("cats sit on mats\ncats chase mice\n")
        self.assertEqual(stats.token_count, 7)
        self.assertEqual(stats.counts["cats"], 2)
        self.assertEqual(stats.counts["mice"], 1)
        self.assertNotIn("", stats.counts)

    def test_clean_mode_ignores_leading_empty_fields(self) -> None:
        stats = tokenize_text(" cats sit\n", count_empty_tokens=False)
        self.assertEqual(stats.token_count, 2)
        self.assertEqual(dict(stats.counts), {"cats": 1, "sit": 1})

    def test_compat_mode_counts_leading_empty_fields(self) -> None:
        stats = tokenize_text(" cats sit\n", count_empty_tokens=True)
        self.assertEqual(stats.token_count, 3)
        self.assertEqual(dict(stats.counts), {"cats": 1, "sit": 1})
        self.assertAlmostEqual(stats.tf()["cats"], 1 / 3)

    def test_blank_lines_do_not_count(self) -> None:
        stats = tokenize_text("cats\n\n\nsit\n")
        self.assertEqual(stats.token_count, 2)

    def test_whitespace_only_line_matches_perl_empty_split(self) -> None:
        self.assertEqual(split_perl_spaces(" "), [])
        stats = tokenize_text("cats\n   \nsit\n", count_empty_tokens=True)
        self.assertEqual(stats.token_count, 2)

    def test_double_spaces_from_punctuation_do_not_create_empty_tokens(self) -> None:
        # "hello, world" -> collapse -> strip comma -> "hello  world"
        stats = tokenize_text("hello, world\n", count_empty_tokens=True)
        self.assertEqual(stats.token_count, 2)
        self.assertEqual(dict(stats.counts), {"hello": 1, "world": 1})

    def test_trailing_space_does_not_inflate_compat_denominator(self) -> None:
        stats = tokenize_text("hello \n", count_empty_tokens=True)
        self.assertEqual(stats.token_count, 1)


if __name__ == "__main__":
    unittest.main()
