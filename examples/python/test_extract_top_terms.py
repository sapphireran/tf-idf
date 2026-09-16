#!/usr/bin/env python3
"""Ranking helper tests against a tiny TSV and the committed Alice table."""

from __future__ import annotations

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import extract_top_terms  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[2]


class LoadAndRankTests(unittest.TestCase):
    def test_sorts_by_score_then_term(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "scores.txt"
            path.write_text("the\t0\ncat\t0.18\nmat\t0.18\non\t0\n", encoding="utf-8")
            rows = extract_top_terms.load_scores(path)
            rows.sort(key=lambda item: (-item[1], item[0]))
            self.assertEqual([term for term, _ in rows], ["cat", "mat", "on", "the"])

    def test_skips_df_header(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "df.txt"
            path.write_text(
                "word \t #docs it exists in \t doc names\ncat\t1\tcats.txt, \n",
                encoding="utf-8",
            )
            rows = extract_top_terms.load_scores(path)
            self.assertEqual(rows, [("cat", 1.0)])

    def test_cli_alice_head(self) -> None:
        path = REPO_ROOT / "output" / "tfidf" / "carroll-alice.txt"
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = extract_top_terms.main([str(path), "-n", "3"])
        self.assertEqual(rc, 0)
        lines = [line for line in buf.getvalue().splitlines() if line[:1].isspace() or line[:1].isdigit()]
        # ranked rows look like "   1   0.02595...  alice"
        joined = buf.getvalue()
        self.assertIn("alice", joined)
        self.assertIn("gryphon", joined)
        self.assertIn("duchess", joined)

    def test_zeros_count(self) -> None:
        path = REPO_ROOT / "output" / "tfidf" / "carroll-alice.txt"
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = extract_top_terms.main([str(path), "--zeros", "-n", "1"])
        self.assertEqual(rc, 0)
        self.assertIn("with score=0", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
