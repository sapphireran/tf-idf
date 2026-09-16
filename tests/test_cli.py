"""CLI smoke tests for compute_tfidf.py and top_terms.py."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from support import MICRO, PYTHON_EXAMPLES, ROOT


def run_cli(script: str, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(PYTHON_EXAMPLES / script), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


class ComputeCliTests(unittest.TestCase):
    def test_writes_expected_layout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            result = run_cli(
                "compute_tfidf.py",
                ["--input-dir", str(MICRO), "--output-dir", str(out)],
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("N=3", result.stdout)
            self.assertTrue((out / "idf.txt").is_file())
            self.assertTrue((out / "df.txt").is_file())
            self.assertTrue((out / "tf" / "d1-cat.txt").is_file())
            self.assertTrue((out / "tfidf" / "d3-bread.txt").is_file())

    def test_missing_input_dir_is_a_clean_error(self) -> None:
        result = run_cli(
            "compute_tfidf.py",
            ["--input-dir", "/no/such/corpus", "--output-dir", "/tmp/out"],
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("not found", result.stderr)


class TopTermsCliTests(unittest.TestCase):
    def test_ranks_checked_in_alice(self) -> None:
        alice = ROOT / "output" / "tfidf" / "carroll-alice.txt"
        result = run_cli("top_terms.py", [str(alice), "--top", "3"])
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = [line for line in result.stdout.splitlines() if line.startswith("  ")]
        self.assertEqual(lines[0].split()[0], "alice")

    def test_directory_mode_lists_each_file(self) -> None:
        result = run_cli(
            "top_terms.py",
            [str(ROOT / "output" / "tfidf"), "--top", "1"],
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("== carroll-alice.txt", result.stdout)
        self.assertIn("== melville-moby_dick.txt", result.stdout)

    def test_missing_path_is_a_clean_error(self) -> None:
        result = run_cli("top_terms.py", ["/no/such/scores.tsv"])
        self.assertEqual(result.returncode, 2)
        self.assertIn("not found", result.stderr)
