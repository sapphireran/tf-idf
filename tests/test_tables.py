"""Gold TSV loader, including the one corrupt IDF hapax row."""

from __future__ import annotations

import math
import unittest
from pathlib import Path

from querydesk.tables import load_tf_tsv, parse_float

ROOT = Path(__file__).resolve().parent.parent


class ParseFloatTests(unittest.TestCase):
    def test_plain_and_scientific(self) -> None:
        self.assertEqual(parse_float("2.89037175789616"), 2.89037175789616)
        self.assertAlmostEqual(parse_float("4.71666965389078e-06"), 4.71666965389078e-06)

    def test_trailing_junk_from_gold_idf(self) -> None:
        self.assertAlmostEqual(parse_float("2.89037175789616y"), math.log(18))


class GoldIdfTests(unittest.TestCase):
    def test_thatyou_recovers_hapax_idf(self) -> None:
        idf = load_tf_tsv(ROOT / "output" / "idf.txt")
        self.assertAlmostEqual(idf["thatyou"], math.log(18))
        self.assertEqual(idf["the"], 0.0)
        self.assertAlmostEqual(idf["alice"], math.log(6))
