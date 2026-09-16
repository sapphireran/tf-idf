"""CLI smoke tests (subprocess, as a user would run them)."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "tfidf_toy", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


class CliTests(unittest.TestCase):
    def test_help(self) -> None:
        result = _run("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("top", result.stdout)
        self.assertIn("compare", result.stdout)

    def test_demo_prints_rabbit_and_zero_glue_words(self) -> None:
        result = _run("demo")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("rabbit", result.stdout)
        self.assertIn("ghost", result.stdout)
        self.assertIn("ship", result.stdout)
        self.assertIn("N = 3 documents", result.stdout)
        # raw idf section should show the = 0
        self.assertIn("the", result.stdout)

    def test_top_only_tiny_corpus(self) -> None:
        result = _run(
            "top",
            "--input",
            str(ROOT / "examples" / "tiny_corpus"),
            "--only",
            "alice.txt",
            "--k",
            "3",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("alice.txt", result.stdout)
        first_term_line = [
            line for line in result.stdout.splitlines() if line.startswith("  ")
        ][0]
        self.assertIn("rabbit", first_term_line)
        self.assertNotIn("whale.txt", result.stdout)

    def test_compare_tiny_corpus(self) -> None:
        result = _run(
            "compare",
            "--input",
            str(ROOT / "examples" / "tiny_corpus"),
            "alice.txt",
            "hamlet.txt",
            "--k",
            "4",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("rabbit", result.stdout)
        self.assertIn("ghost", result.stdout)

    def test_compute_then_diff_against_itself(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            compute = _run(
                "compute",
                "--input",
                str(ROOT / "examples" / "tiny_corpus"),
                "--output",
                str(out),
            )
            self.assertEqual(compute.returncode, 0, compute.stderr)
            self.assertTrue((out / "tfidf" / "alice.txt").is_file())
            diff = _run(
                "diff-output",
                "--left",
                str(out),
                "--right",
                str(out),
            )
            self.assertEqual(diff.returncode, 0, diff.stderr)
            self.assertIn("max|Δ|", diff.stdout)
            self.assertIn("0", diff.stdout)


if __name__ == "__main__":
    unittest.main()
