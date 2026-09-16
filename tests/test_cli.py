import unittest
from io import StringIO
from unittest.mock import patch

from shelf_units.cli import main


class CliTests(unittest.TestCase):
    def test_demo_exits_zero_and_mentions_alice(self):
        buf = StringIO()
        with patch("sys.stdout", buf):
            code = main(["demo"])
        self.assertEqual(code, 0)
        out = buf.getvalue()
        self.assertIn("alice-vii", out)
        self.assertIn("01-darkroom", out)

    def test_commonplace_query(self):
        buf = StringIO()
        with patch("sys.stdout", buf):
            code = main(["commonplace", "hypo fixer enlarger", "-k", "2"])
        self.assertEqual(code, 0)
        self.assertIn("01-darkroom", buf.getvalue())

    def test_bible_single_book(self):
        buf = StringIO()
        with patch("sys.stdout", buf):
            code = main(["bible", "--book", "genesis", "-k", "4"])
        self.assertEqual(code, 0)
        self.assertGreater(len(buf.getvalue().strip().splitlines()), 1)

    def test_rank_gutenberg_alice_query(self):
        buf = StringIO()
        with patch("sys.stdout", buf):
            code = main(["rank", "alice rabbit queen", "--units", "gutenberg", "-k", "3"])
        self.assertEqual(code, 0)
        self.assertIn("carroll-alice", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
