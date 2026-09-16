"""CLI smoke tests: write tiny-corpus tables and rank / compare them."""

from __future__ import annotations

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

_EXAMPLES_PYTHON = Path(__file__).resolve().parents[1]
_REPO_ROOT = _EXAMPLES_PYTHON.parents[1]
if str(_EXAMPLES_PYTHON) not in sys.path:
    sys.path.insert(0, str(_EXAMPLES_PYTHON))

import rank_terms  # noqa: E402
import similar_docs  # noqa: E402
import tfidf_toy  # noqa: E402


TINY = _REPO_ROOT / "examples" / "tiny-corpus" / "documents"
ALICE = _REPO_ROOT / "output" / "tfidf" / "carroll-alice.txt"
EMMA = _REPO_ROOT / "output" / "tfidf" / "austen-emma.txt"
SENSE = _REPO_ROOT / "output" / "tfidf" / "austen-sense.txt"


class CliSmokeTests(unittest.TestCase):
    def test_tfidf_toy_writes_expected_layout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = tfidf_toy.main([str(TINY), "--write-dir", str(dest), "--top", "3"])
            self.assertEqual(rc, 0)
            out = buf.getvalue()
            self.assertIn("N=4", out)
            self.assertIn("bread", out)
            self.assertTrue((dest / "idf.txt").is_file())
            self.assertTrue((dest / "df.txt").is_file())
            self.assertTrue((dest / "tf" / "01-bakery-morning.txt").is_file())
            self.assertTrue((dest / "tfidf" / "04-rehearsal-room.txt").is_file())
            # Rank from the just-written table.
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = rank_terms.main(
                    ["--from-table", str(dest / "tfidf" / "02-ridge-trail.txt"), "--top", "3"]
                )
            self.assertEqual(rc, 0)
            self.assertIn("trail", buf.getvalue())

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = similar_docs.main(["--table-dir", str(dest / "tfidf"), "--matrix"])
            self.assertEqual(rc, 0)
            text = buf.getvalue()
            self.assertIn("01-bakery-morning.txt", text)
            self.assertIn("0.2508", text)

    def test_rank_committed_alice(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = rank_terms.main(["--from-table", str(ALICE), "--top", "5"])
        self.assertEqual(rc, 0)
        lines = [line for line in buf.getvalue().splitlines() if line.startswith("    1")]
        self.assertTrue(any("alice" in line for line in lines))

    def test_similar_two_austen_tables(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = similar_docs.main(["--tables", str(EMMA), str(SENSE)])
        self.assertEqual(rc, 0)
        self.assertIn("austen-emma.txt", buf.getvalue())
        # Two Austen novels should not be orthogonal.
        score_line = buf.getvalue().splitlines()[1]
        score = float(score_line.split()[0])
        self.assertGreater(score, 0.05)

    def test_rank_missing_file(self) -> None:
        self.assertEqual(rank_terms.main(["--from-table", "/no/such/table.txt"]), 2)


if __name__ == "__main__":
    unittest.main()
