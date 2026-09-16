"""Lock the hand-calculation floats and a few tokenizer rules."""

from __future__ import annotations

import importlib.util
import math
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "examples" / "tiny-corpus" / "compute_tfidf.py"


def load_compute_module():
    name = "tiny_corpus_compute_tfidf"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


compute = load_compute_module()


def collection_from_texts(mapping: dict[str, str]):
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp)
        for name, text in mapping.items():
            (folder / name).write_text(text + "\n", encoding="utf-8")
        return compute.load_collection(folder)


class TokenizeTests(unittest.TestCase):
    def test_lowercase_and_drop_punctuation(self) -> None:
        self.assertEqual(compute.tokenize("Alice's Adventures!"), ["alices", "adventures"])

    def test_digits_survive(self) -> None:
        self.assertEqual(compute.tokenize("Carroll 1865"), ["carroll", "1865"])

    def test_empty_and_whitespace_only_lines(self) -> None:
        self.assertEqual(compute.tokenize("tea\n\n  \nkettle"), ["tea", "kettle"])


class HandCalculationTests(unittest.TestCase):
    """Numbers from examples/hand-calculation.md."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.col = collection_from_texts(
            {
                "d1.txt": "the tea is hot",
                "d2.txt": "the storm is loud",
                "d3.txt": "hot tea and tea leaves",
            }
        )
        cls.by_name = {doc.name: doc for doc in cls.col.documents}

    def test_n_is_three(self) -> None:
        self.assertEqual(self.col.n_docs, 3)

    def test_token_counts(self) -> None:
        self.assertEqual(self.by_name["d1.txt"].n_tokens, 4)
        self.assertEqual(self.by_name["d2.txt"].n_tokens, 4)
        self.assertEqual(self.by_name["d3.txt"].n_tokens, 5)
        self.assertEqual(self.by_name["d3.txt"].counts["tea"], 2)

    def test_document_frequencies(self) -> None:
        self.assertEqual(self.col.df("tea"), 2)
        self.assertEqual(self.col.df("storm"), 1)
        self.assertEqual(self.col.df("and"), 1)
        self.assertEqual(self.col.df("the"), 2)

    def test_idf_raw_values(self) -> None:
        self.assertAlmostEqual(self.col.idf_raw("tea"), math.log(1.5), places=12)
        self.assertAlmostEqual(self.col.idf_raw("and"), math.log(3), places=12)
        self.assertAlmostEqual(self.col.idf_raw("tea"), 0.4054651081, places=10)
        self.assertAlmostEqual(self.col.idf_raw("and"), 1.0986122887, places=10)

    def test_d1_is_a_four_way_tie(self) -> None:
        doc = self.by_name["d1.txt"]
        scores = {term: self.col.tfidf(term, doc) for term in doc.counts}
        self.assertEqual(len(set(round(v, 12) for v in scores.values())), 1)
        self.assertAlmostEqual(scores["tea"], 0.1013662770, places=10)

    def test_d2_unique_weather_words_win(self) -> None:
        doc = self.by_name["d2.txt"]
        storm = self.col.tfidf("storm", doc)
        loud = self.col.tfidf("loud", doc)
        the = self.col.tfidf("the", doc)
        self.assertAlmostEqual(storm, 0.2746530722, places=10)
        self.assertAlmostEqual(loud, storm, places=12)
        self.assertGreater(storm, the)

    def test_d3_unique_and_beats_repeated_tea(self) -> None:
        doc = self.by_name["d3.txt"]
        tea = self.col.tfidf("tea", doc)
        and_ = self.col.tfidf("and", doc)
        leaves = self.col.tfidf("leaves", doc)
        hot = self.col.tfidf("hot", doc)
        self.assertAlmostEqual(tea, 0.1621860432, places=10)
        self.assertAlmostEqual(and_, 0.2197224577, places=10)
        self.assertAlmostEqual(leaves, and_, places=12)
        self.assertGreater(and_, tea)
        self.assertGreater(tea, hot)

    def test_smoothing_flips_d3_winner_to_tea(self) -> None:
        doc = self.by_name["d3.txt"]
        tea_smooth = doc.tf("tea") * self.col.idf_smooth("tea")
        and_smooth = doc.tf("and") * self.col.idf_smooth("and")
        self.assertGreater(tea_smooth, and_smooth)

    def test_term_in_every_document_has_zero_idf(self) -> None:
        col = collection_from_texts({"a.txt": "shared only", "b.txt": "shared too"})
        self.assertEqual(col.idf_raw("shared"), 0.0)
        self.assertEqual(col.tfidf("shared", col.documents[0]), 0.0)


class TinyCorpusSmokeTests(unittest.TestCase):
    def test_five_themed_documents_load(self) -> None:
        docs = ROOT / "examples" / "tiny-corpus" / "documents"
        col = compute.load_collection(docs)
        self.assertEqual(col.n_docs, 5)
        names = {doc.name for doc in col.documents}
        self.assertEqual(
            names,
            {
                "tea-garden.txt",
                "tea-ceremony.txt",
                "harbor-storm.txt",
                "lighthouse-night.txt",
                "chess-lesson.txt",
            },
        )
        self.assertGreaterEqual(col.df("tea"), 2)
        self.assertLess(col.df("tea"), 5)
        self.assertEqual(col.df("knight"), 1)
        self.assertEqual(col.df("harbor"), 2)

    def test_stoplist_promotes_theme_words_in_chess(self) -> None:
        docs = ROOT / "examples" / "tiny-corpus" / "documents"
        raw = compute.load_collection(docs, stop=False)
        stopped = compute.load_collection(docs, stop=True)
        chess_raw = next(doc for doc in raw.documents if doc.name == "chess-lesson.txt")
        chess_stop = next(doc for doc in stopped.documents if doc.name == "chess-lesson.txt")
        raw_top = raw.tfidf("i", chess_raw)
        # "i" is in the stoplist, so it must disappear from the stopped doc.
        self.assertNotIn("i", chess_stop.counts)
        knight = stopped.tfidf("knight", chess_stop)
        king = stopped.tfidf("king", chess_stop)
        self.assertGreater(knight, 0)
        self.assertGreater(king, 0)
        self.assertGreater(raw_top, raw.tfidf("knight", chess_raw))

    def test_write_outputs_creates_expected_layout(self) -> None:
        docs = ROOT / "examples" / "tiny-corpus" / "documents"
        col = compute.load_collection(docs)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            compute.write_outputs(col, out)
            self.assertTrue((out / "idf.txt").is_file())
            self.assertTrue((out / "df.txt").is_file())
            self.assertTrue((out / "tf" / "chess-lesson.txt").is_file())
            self.assertTrue((out / "tfidf" / "tea-garden.txt").is_file())
            idf_terms = [line.split("\t")[0] for line in (out / "idf.txt").read_text().splitlines()]
            self.assertIn("tea", idf_terms)
            self.assertIn("knight", idf_terms)


if __name__ == "__main__":
    unittest.main()
