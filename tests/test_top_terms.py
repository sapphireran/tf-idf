"""Smoke-test the ranking printer against a two-file TSV directory."""

from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "examples" / "top_terms.py"


def load_top_terms():
    name = "examples_top_terms"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


top_terms = load_top_terms()


class TopTermsTests(unittest.TestCase):
    def test_sorts_descending_and_limits_n(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "alice.txt").write_text("alice\t0.02\nthe\t0.0\ngryphon\t0.004\n", encoding="utf-8")
            (folder / "skip.me").write_text("ignored\n", encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = top_terms.main(["--path", str(folder), "--n", "2"])
            self.assertEqual(code, 0)
            text = buf.getvalue()
            self.assertIn("== alice.txt", text)
            lines = [line for line in text.splitlines() if line and not line.startswith("==")]
            self.assertEqual(len(lines), 2)
            self.assertTrue(lines[0].startswith("alice"))
            self.assertTrue(lines[1].startswith("gryphon"))

    def test_files_filter_rejects_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "a.txt").write_text("x\t1\n", encoding="utf-8")
            with self.assertRaises(SystemExit):
                top_terms.main(["--path", str(folder), "--files", "missing.txt"])


if __name__ == "__main__":
    unittest.main()
