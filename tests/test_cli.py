"""CLI smoke tests for the personal query desk."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "querydesk", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


class CliTests(unittest.TestCase):
    def test_field_notes_help(self) -> None:
        proc = run("field-notes", "--query", "cairn moraine icefall")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("glacier-cairn.txt", proc.stdout)
        self.assertIn("cairn", proc.stdout)

    def test_top_alice(self) -> None:
        proc = run("top", "--doc", "carroll-alice.txt", "--n", "5")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("alice", proc.stdout.lower())

    def test_compare_variants(self) -> None:
        proc = run(
            "compare",
            "cairn icefall",
            "--corpus",
            str(ROOT / "examples" / "field-notes" / "texts"),
            "--variants",
            "classic,smooth,bm25",
            "--top",
            "2",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("[classic]", proc.stdout)
        self.assertIn("[smooth]", proc.stdout)
        self.assertIn("[bm25]", proc.stdout)
        self.assertIn("glacier-cairn.txt", proc.stdout)

    def test_self_test(self) -> None:
        proc = run("self-test")
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        self.assertIn("self-test ok", proc.stdout)
