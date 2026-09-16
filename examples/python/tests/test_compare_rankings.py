"""Fresh vs committed ranking overlap."""

from __future__ import annotations

import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

_EXAMPLES_PYTHON = Path(__file__).resolve().parents[1]
_REPO_ROOT = _EXAMPLES_PYTHON.parents[1]
if str(_EXAMPLES_PYTHON) not in sys.path:
    sys.path.insert(0, str(_EXAMPLES_PYTHON))

import compare_rankings  # noqa: E402
from tfidf_toy import score_corpus  # noqa: E402


TINY = _REPO_ROOT / "examples" / "tiny-corpus" / "documents"
TINY_TFIDF = _REPO_ROOT / "examples" / "tiny-corpus" / "output" / "tfidf"
GUTENBERG = _REPO_ROOT / "gutenberg"
COMMITTED = _REPO_ROOT / "output" / "tfidf"


class CompareRankingsTests(unittest.TestCase):
    def test_self_overlap_is_one(self) -> None:
        scores = score_corpus(TINY)
        alice = compare_rankings.compare_book(
            scores.by_name()["01-bakery-morning.txt"].tfidf,
            TINY_TFIDF / "01-bakery-morning.txt",
            top=6,
        )
        self.assertTrue(alice["same_top"])
        self.assertEqual(alice["overlap"], 1.0)

    def test_gutenberg_alice_same_top_term(self) -> None:
        scores = score_corpus(GUTENBERG)
        row = compare_rankings.compare_book(
            scores.by_name()["carroll-alice.txt"].tfidf,
            COMMITTED / "carroll-alice.txt",
            top=10,
        )
        self.assertEqual(row["fresh"][0], "alice")
        self.assertEqual(row["committed"][0], "alice")
        self.assertGreaterEqual(row["overlap"], 0.8)

    def test_cli_tiny_corpus(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = compare_rankings.main(
                [
                    "--corpus",
                    str(TINY),
                    "--committed-dir",
                    str(TINY_TFIDF),
                    "--top",
                    "5",
                ]
            )
        self.assertEqual(rc, 0)
        self.assertIn("01-bakery-morning.txt", buf.getvalue())
        self.assertIn("yes", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
