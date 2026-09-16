"""CLI smoke tests. These are the commands the notebook tells me to run."""

from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout

from tfidf.cli import main


class CliTests(unittest.TestCase):
    def _run(self, *argv: str) -> str:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(list(argv))
        self.assertEqual(code, 0, buf.getvalue())
        return buf.getvalue()

    def test_demo(self) -> None:
        out = self._run("demo")
        self.assertIn("doc_cats.txt", out)
        self.assertIn("cat", out)
        self.assertIn("distant telescopes", out)

    def test_rank_tiny(self) -> None:
        out = self._run("rank", "cat mat", "--corpus", "tiny", "-k", "2")
        self.assertIn("doc_cats.txt", out)
        self.assertIn("cosine", out)

    def test_compare(self) -> None:
        out = self._run("compare", "cat", "--corpus", "tiny", "-k", "2")
        self.assertIn("cosine/classic", out)
        self.assertIn("bm25", out)

    def test_explain(self) -> None:
        out = self._run(
            "explain",
            "cat",
            "--doc",
            "examples/tiny_corpus/doc_cats.txt",
        )
        self.assertIn("raw_tf=2", out)
        self.assertIn("classic", out)

    def test_corpus_stats(self) -> None:
        out = self._run("corpus-stats", "--corpus", "tiny")
        self.assertIn("N=4", out)

    def test_tokens(self) -> None:
        out = self._run("tokens", "--doc", "examples/tiny_corpus/doc_stars.txt")
        self.assertIn("telescopes", out)

    def test_unknown_corpus(self) -> None:
        buf = io.StringIO()
        # errors go to stderr; just check the exit code
        code = main(["rank", "cat", "--corpus", "does-not-exist"])
        self.assertEqual(code, 2)
        del buf

    def test_help(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            main(["--help"])
        self.assertEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
