import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from tfidf.cli import main


class CliTests(unittest.TestCase):
    def test_query_ranks_jupiter(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(
                [
                    "query",
                    "examples/tiny-corpus",
                    "ganymede telescope opposition",
                ]
            )
        self.assertEqual(code, 0)
        first = buf.getvalue().splitlines()[0]
        self.assertIn("jupiter.txt", first)

    def test_report_includes_heading(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(["report", "examples/hand-calculation/corpus", "-n", "3"])
        self.assertEqual(code, 0)
        body = buf.getvalue()
        self.assertIn("# TF-IDF report", body)
        self.assertIn("doc-a.txt", body)
        self.assertIn("mat", body)

    def test_compute_writes_expected_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = main(
                    [
                        "compute",
                        "examples/hand-calculation/corpus",
                        "-o",
                        str(out),
                    ]
                )
            self.assertEqual(code, 0)
            self.assertTrue((out / "idf.txt").is_file())
            self.assertTrue((out / "tfidf" / "doc-a.txt").is_file())
            self.assertTrue((out / "tf" / "doc-c.txt").is_file())

    def test_top_tsv_reads_committed_alice(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(["top-tsv", "output/tfidf", "-n", "3"])
        self.assertEqual(code, 0)
        body = buf.getvalue()
        self.assertIn("carroll-alice.txt", body)
        self.assertIn("alice", body)


if __name__ == "__main__":
    unittest.main()
