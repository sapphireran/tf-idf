"""Four workshop notes: tables, rankings, expected TSV files."""

from __future__ import annotations

import math
import unittest
from pathlib import Path

from querydesk.index import build_index, write_index_tables
from querydesk.query import rank
from querydesk.tables import load_tf_tsv

ROOT = Path(__file__).resolve().parent.parent
TEXTS = ROOT / "examples" / "field-notes" / "texts"
EXPECTED = ROOT / "examples" / "field-notes" / "expected"

QUERIES = {
    "cairn moraine icefall": "glacier-cairn.txt",
    "chase quoins tympan": "letterpress-proof.txt",
    "stilling datum slack": "tide-gauge.txt",
    "voucher blotters silica": "herbarium-press.txt",
}


class FieldNotesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.index = build_index(TEXTS, variant="classic", n_mode="texts")

    def test_n_is_four(self) -> None:
        self.assertEqual(self.index.n, 4)
        self.assertEqual(len(self.index.docs), 4)

    def test_universal_the_and_a(self) -> None:
        self.assertEqual(self.index.df["the"], 4)
        self.assertEqual(self.index.df["a"], 4)
        self.assertEqual(self.index.idf["the"], 0.0)
        self.assertEqual(self.index.idf["a"], 0.0)

    def test_cairn_is_hapax(self) -> None:
        self.assertEqual(self.index.df["cairn"], 1)
        self.assertAlmostEqual(self.index.idf["cairn"], math.log(4))

    def test_glacier_word_count_and_cairn_weight(self) -> None:
        doc = self.index.docs["glacier-cairn.txt"]
        self.assertEqual(doc.word_count, 23)
        self.assertEqual(doc.raw_tf["cairn"], 3)
        self.assertAlmostEqual(doc.tf["cairn"], 3 / 23)
        self.assertAlmostEqual(doc.tfidf["cairn"], (3 / 23) * math.log(4))
        self.assertEqual(doc.tfidf["the"], 0.0)

    def test_themed_queries_isolate_one_note(self) -> None:
        for query, winner in QUERIES.items():
            hits = rank(query, self.index, score="cosine")
            self.assertEqual(hits[0].name, winner, query)
            self.assertGreater(hits[0].score, 0.3, query)
            for hit in hits[1:]:
                self.assertEqual(hit.score, 0.0, f"{query} vs {hit.name}")

    def test_universal_query_is_flat_zero(self) -> None:
        hits = rank("the", self.index, score="cosine")
        self.assertTrue(all(hit.score == 0.0 for hit in hits))

    def test_expected_tables_if_present(self) -> None:
        idf_path = EXPECTED / "idf.txt"
        if not idf_path.exists():
            self.skipTest("expected tables not written yet")
        gold_idf = load_tf_tsv(idf_path)
        self.assertEqual(set(gold_idf), set(self.index.idf))
        for term, value in gold_idf.items():
            self.assertAlmostEqual(self.index.idf[term], value, places=12)
        glacier = load_tf_tsv(EXPECTED / "tfidf" / "glacier-cairn.txt")
        built = self.index.docs["glacier-cairn.txt"].tfidf
        for term, value in glacier.items():
            self.assertAlmostEqual(built[term], value, places=12)
