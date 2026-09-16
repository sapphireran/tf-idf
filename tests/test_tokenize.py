"""Tokenizer matches tf-idf-values.pl, including empty split fields."""

from __future__ import annotations

import math
import unittest
from pathlib import Path

from querydesk.tables import load_tf_tsv
from querydesk.tokenize import count_path, count_text, normalize_line, split_fields

ROOT = Path(__file__).resolve().parent.parent
ALICE = ROOT / "gutenberg" / "carroll-alice.txt"
GOLD_TF = ROOT / "output" / "tf" / "carroll-alice.txt"


class NormalizeTests(unittest.TestCase):
    def test_lower_and_punctuation(self) -> None:
        self.assertEqual(normalize_line("Alice's Adventures!"), "alices adventures")

    def test_chomp_and_collapse(self) -> None:
        self.assertEqual(normalize_line("Hello   world\n"), "hello world")

    def test_leading_space_survives_collapse(self) -> None:
        self.assertEqual(normalize_line("  Cairn ice"), " cairn ice")


class SplitTests(unittest.TestCase):
    def test_leading_empty_field(self) -> None:
        self.assertEqual(split_fields(" cairn ice"), ["", "cairn", "ice"])

    def test_trailing_empty_dropped(self) -> None:
        self.assertEqual(split_fields("cairn ice "), ["cairn", "ice"])

    def test_empty_line(self) -> None:
        self.assertEqual(split_fields(""), [])


class WordCountTests(unittest.TestCase):
    def test_empty_field_inflates_denominator(self) -> None:
        counts, word_count = count_text(" cairn ice")
        self.assertEqual(word_count, 3)
        self.assertEqual(counts, {"cairn": 1, "ice": 1})
        self.assertAlmostEqual(counts["cairn"] / word_count, 1 / 3)

    def test_alice_matches_gold_tf_table(self) -> None:
        counts, word_count = count_path(ALICE)
        gold = load_tf_tsv(GOLD_TF)
        self.assertEqual(word_count, 26576)
        self.assertEqual(set(counts), set(gold))
        self.assertEqual(counts["alice"], 385)
        max_delta = max(abs(counts[term] / word_count - gold[term]) for term in gold)
        self.assertLess(max_delta, 1e-14)


if __name__ == "__main__":
    unittest.main()
