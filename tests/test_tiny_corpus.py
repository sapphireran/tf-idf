"""Pinned floats from docs/worked-example.md."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tfidf_toy.model import SMOOTH, TfIdfIndex, idf_value

LN3 = math.log(3)
TINY = ROOT / "examples" / "tiny_corpus"


class IdfFormulaTests(unittest.TestCase):
    def test_raw_everywhere_is_zero(self) -> None:
        self.assertEqual(idf_value(3, 3, "raw"), 0.0)

    def test_raw_hapax_is_ln_n(self) -> None:
        self.assertAlmostEqual(idf_value(3, 1, "raw"), LN3, places=12)
        self.assertAlmostEqual(idf_value(18, 1, "raw"), math.log(18), places=12)

    def test_smooth_everywhere_is_one(self) -> None:
        self.assertAlmostEqual(idf_value(3, 3, "smooth"), 1.0, places=12)

    def test_smooth_hapax(self) -> None:
        self.assertAlmostEqual(idf_value(3, 1, "smooth"), math.log(2) + 1.0, places=12)

    def test_rejects_bad_inputs(self) -> None:
        with self.assertRaises(ValueError):
            idf_value(3, 0, "raw")
        with self.assertRaises(ValueError):
            idf_value(3, 1, "bm25")


class TinyCorpusRawTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.index = TfIdfIndex.from_directory(TINY, idf_mode="raw")

    def test_collection_size_and_shared_terms(self) -> None:
        self.assertEqual(self.index.n_docs, 3)
        for glue in ("the", "was", "late"):
            self.assertEqual(self.index.df[glue], 3)
            self.assertEqual(self.index.idf[glue], 0.0)

    def test_unique_terms_have_idf_ln3(self) -> None:
        for term in ("alice", "rabbit", "whale", "ship", "hamlet", "ghost"):
            self.assertEqual(self.index.df[term], 1)
            self.assertAlmostEqual(self.index.idf[term], LN3, places=12)

    def test_alice_document_scores(self) -> None:
        doc = self.index.get("alice.txt")
        self.assertEqual(doc.length, 8)
        self.assertAlmostEqual(doc.tf["rabbit"], 0.25, places=12)
        self.assertAlmostEqual(doc.tfidf["rabbit"], 0.25 * LN3, places=12)
        self.assertAlmostEqual(doc.tfidf["alice"], 0.125 * LN3, places=12)
        self.assertAlmostEqual(doc.tfidf["chased"], 0.125 * LN3, places=12)
        self.assertEqual(doc.tfidf["the"], 0.0)
        self.assertEqual(doc.tfidf["late"], 0.0)
        top = [term for term, _ in doc.top_terms(3)]
        self.assertEqual(top[0], "rabbit")
        self.assertEqual(set(top[1:]), {"alice", "chased"})

    def test_whale_document_scores(self) -> None:
        doc = self.index.get("whale.txt")
        self.assertEqual(doc.length, 9)
        self.assertAlmostEqual(doc.tfidf["ship"], (2 / 9) * LN3, places=12)
        self.assertAlmostEqual(doc.tfidf["whale"], (1 / 9) * LN3, places=12)
        self.assertEqual(doc.top_terms(1)[0][0], "ship")

    def test_hamlet_document_scores(self) -> None:
        doc = self.index.get("hamlet.txt")
        self.assertEqual(doc.length, 8)
        self.assertAlmostEqual(doc.tfidf["ghost"], 0.25 * LN3, places=12)
        self.assertEqual(doc.top_terms(1)[0][0], "ghost")

    def test_pinned_floats_from_the_doc(self) -> None:
        alice = self.index.get("alice.txt")
        whale = self.index.get("whale.txt")
        self.assertAlmostEqual(alice.tfidf["rabbit"], 0.27465307216702745, places=12)
        self.assertAlmostEqual(alice.tfidf["alice"], 0.13732653608351372, places=12)
        self.assertAlmostEqual(whale.tfidf["ship"], 0.24413606414846885, places=12)
        self.assertAlmostEqual(whale.tfidf["whale"], 0.12206803207423442, places=12)

    def test_compare_alice_vs_whale(self) -> None:
        left, right = self.index.compare("alice.txt", "whale.txt", k=3)
        self.assertEqual(left[0][0], "rabbit")
        self.assertEqual(right[0][0], "ship")
        self.assertGreater(left[0][3], 0)
        self.assertGreater(right[0][3], 0)

    def test_write_and_reload_legacy_layout(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            self.index.write_legacy_output(out)
            self.assertTrue((out / "idf.txt").is_file())
            self.assertTrue((out / "df.txt").is_file())
            self.assertTrue((out / "tf" / "alice.txt").is_file())
            self.assertTrue((out / "tfidf" / "whale.txt").is_file())
            idf_line = [
                line
                for line in (out / "idf.txt").read_text().splitlines()
                if line.startswith("the\t")
            ][0]
            self.assertEqual(idf_line, "the\t0")


class TinyCorpusSmoothTests(unittest.TestCase):
    def test_shared_terms_are_nonzero(self) -> None:
        index = TfIdfIndex.from_directory(TINY, idf_mode=SMOOTH)
        doc = index.get("alice.txt")
        self.assertAlmostEqual(index.idf["the"], 1.0, places=12)
        self.assertGreater(doc.tfidf["the"], 0.0)
        # rabbit still outranks the, because df is lower even after smoothing
        scores = dict(doc.top_terms(-1))
        self.assertGreater(scores["rabbit"], scores["the"])


if __name__ == "__main__":
    unittest.main()
