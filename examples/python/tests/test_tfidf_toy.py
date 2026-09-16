"""Exact arithmetic checks for the tiny corpus and the tokenizer."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

_EXAMPLES_PYTHON = Path(__file__).resolve().parents[1]
_REPO_ROOT = _EXAMPLES_PYTHON.parents[1]
if str(_EXAMPLES_PYTHON) not in sys.path:
    sys.path.insert(0, str(_EXAMPLES_PYTHON))

from tfidf_toy import (  # noqa: E402
    iter_corpus_files,
    score_corpus,
    score_tokens,
    tokenize_line,
    tokenize_text,
)


TINY = _REPO_ROOT / "examples" / "tiny-corpus" / "documents"
LN2 = math.log(2)
LN4 = math.log(4)


class TokenizeTests(unittest.TestCase):
    def test_title_case_and_period(self) -> None:
        self.assertEqual(
            tokenize_line("The baker scored the bread and the bread cracked."),
            ["the", "baker", "scored", "the", "bread", "and", "the", "bread", "cracked"],
        )

    def test_possessive_and_contraction(self) -> None:
        # Same collapsing the Perl regexes apply: Alice's -> alices, I'm -> im.
        self.assertEqual(tokenize_line("Alice's I'm"), ["alices", "im"])

    def test_hyphen_glues(self) -> None:
        self.assertEqual(tokenize_line("waistcoat-pocket"), ["waistcoatpocket"])

    def test_blank_line_is_empty_token(self) -> None:
        self.assertEqual(tokenize_line(""), [""])

    def test_count_empties_changes_length_only(self) -> None:
        text = "Alice\n\nRabbit"
        clean = tokenize_text(text, count_empties=False)
        legacy = tokenize_text(text, count_empties=True)
        self.assertEqual(clean, ["alice", "rabbit"])
        self.assertGreater(len(legacy), len(clean))
        self.assertEqual([token for token in legacy if token], clean)


class TinyCorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scores = score_corpus(TINY)
        cls.by_name = cls.scores.by_name()

    def test_four_documents_nine_tokens(self) -> None:
        self.assertEqual(self.scores.n_documents, 4)
        for doc in self.scores.documents:
            self.assertEqual(doc.length, 9, doc.name)

    def test_idf_values(self) -> None:
        idf = self.scores.idf
        self.assertEqual(idf["the"], 0.0)
        self.assertEqual(idf["and"], 0.0)
        self.assertAlmostEqual(idf["baker"], LN2, places=12)
        self.assertAlmostEqual(idf["bread"], LN2, places=12)
        self.assertAlmostEqual(idf["followed"], LN2, places=12)
        self.assertAlmostEqual(idf["rose"], LN2, places=12)
        self.assertAlmostEqual(idf["trail"], LN4, places=12)
        self.assertAlmostEqual(idf["song"], LN4, places=12)
        self.assertEqual(self.scores.df["baker"], 2)
        self.assertEqual(self.scores.df["the"], 4)
        self.assertEqual(self.scores.df["scored"], 1)

    def test_morning_bakery_weights(self) -> None:
        weights = self.by_name["01-bakery-morning.txt"].tfidf
        self.assertAlmostEqual(weights["bread"], (2 / 9) * LN2, places=12)
        self.assertAlmostEqual(weights["scored"], (1 / 9) * LN4, places=12)
        self.assertAlmostEqual(weights["cracked"], (1 / 9) * LN4, places=12)
        self.assertAlmostEqual(weights["baker"], (1 / 9) * LN2, places=12)
        self.assertEqual(weights["the"], 0.0)
        self.assertEqual(weights["and"], 0.0)
        # 2/9 ln 2 == 1/9 ln 4: double mention of a df=2 word ties a hapax.
        self.assertAlmostEqual(weights["bread"], weights["scored"], places=12)

    def test_trail_top_term_is_trail(self) -> None:
        weights = self.by_name["02-ridge-trail.txt"].tfidf
        top = max(weights, key=weights.get)
        self.assertEqual(top, "trail")
        self.assertAlmostEqual(weights["trail"], (2 / 9) * LN4, places=12)

    def test_iter_skips_dotfiles(self) -> None:
        names = [path.name for path in iter_corpus_files(TINY)]
        self.assertEqual(
            names,
            [
                "01-bakery-morning.txt",
                "02-ridge-trail.txt",
                "03-bakery-afternoon.txt",
                "04-rehearsal-room.txt",
            ],
        )


class ScoreTokensGuardTests(unittest.TestCase):
    def test_empty_corpus_raises(self) -> None:
        with self.assertRaises(ValueError):
            score_tokens({})

    def test_empty_document_raises(self) -> None:
        with self.assertRaises(ValueError):
            score_tokens({"blank.txt": []})


if __name__ == "__main__":
    unittest.main()
