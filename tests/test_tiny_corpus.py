"""Hand-worked three-document corpus."""

from __future__ import annotations

from math import log
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tests.support import TINY_DOCS, TINY_EXPECTED
from tfidfkit.similarity import cosine, rank_neighbors
from tfidfkit.tables import read_idf, read_token_weights, write_pipeline_tree
from tfidfkit.weights import run_pipeline

LN_3 = log(3)
LN_3_2 = log(3 / 2)


class TinyCorpusMathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = run_pipeline(TINY_DOCS)

    def test_document_set(self) -> None:
        self.assertEqual(self.result.documents, ("birds.txt", "cats.txt", "dogs.txt"))
        self.assertEqual(self.result.n_documents, 3)

    def test_token_counts(self) -> None:
        for name in self.result.documents:
            self.assertEqual(self.result.stats[name].token_count, 7)
        self.assertEqual(self.result.stats["cats.txt"].counts["cats"], 2)
        self.assertEqual(self.result.stats["dogs.txt"].counts["dogs"], 2)
        self.assertEqual(self.result.stats["birds.txt"].counts["birds"], 2)

    def test_document_frequencies(self) -> None:
        df = {token: len(docs) for token, docs in self.result.df.items()}
        self.assertEqual(df["chase"], 3)
        self.assertEqual(df["cats"], 2)
        self.assertEqual(df["mice"], 1)
        self.assertEqual(df["dogs"], 1)
        self.assertEqual(df["birds"], 1)
        self.assertEqual(len(df), 12)

    def test_idf_values(self) -> None:
        self.assertEqual(self.result.idf["chase"], 0.0)
        self.assertAlmostEqual(self.result.idf["cats"], LN_3_2)
        self.assertAlmostEqual(self.result.idf["mice"], LN_3)
        self.assertAlmostEqual(self.result.idf["dogs"], LN_3)

    def test_tfidf_rank_in_cats(self) -> None:
        weights = self.result.tfidf["cats.txt"]
        self.assertAlmostEqual(weights["mice"], (1 / 7) * LN_3)
        self.assertAlmostEqual(weights["cats"], (2 / 7) * LN_3_2)
        self.assertAlmostEqual(weights["sit"], (1 / 7) * LN_3_2)
        self.assertEqual(weights["chase"], 0.0)
        ranked = sorted(weights, key=lambda token: (-weights[token], token))
        self.assertEqual(ranked[0], "mice")
        self.assertEqual(ranked[1], "cats")

    def test_unique_animal_dominates_its_own_file(self) -> None:
        self.assertAlmostEqual(self.result.tfidf["dogs.txt"]["dogs"], (2 / 7) * LN_3)
        self.assertAlmostEqual(self.result.tfidf["birds.txt"]["birds"], (2 / 7) * LN_3)

    def test_cosine_matches_walkthrough(self) -> None:
        cats = self.result.tfidf["cats.txt"]
        dogs = self.result.tfidf["dogs.txt"]
        birds = self.result.tfidf["birds.txt"]
        self.assertAlmostEqual(cosine(cats, dogs), 0.22857179688308324)
        self.assertEqual(cosine(cats, birds), 0.0)
        self.assertEqual(cosine(dogs, birds), 0.0)

    def test_chase_does_not_create_a_neighbor(self) -> None:
        pairs = {frozenset((a, b)): score for a, b, score in rank_neighbors(self.result.tfidf)}
        self.assertEqual(pairs[frozenset(("birds.txt", "cats.txt"))], 0.0)
        self.assertGreater(pairs[frozenset(("cats.txt", "dogs.txt"))], 0.2)


class TinyCorpusExpectedFilesTests(unittest.TestCase):
    def test_expected_idf_matches_pipeline(self) -> None:
        result = run_pipeline(TINY_DOCS)
        expected, dirty = read_idf(TINY_EXPECTED / "idf.txt")
        self.assertEqual(dirty, ())
        self.assertEqual(set(expected), set(result.idf))
        for token, value in expected.items():
            self.assertAlmostEqual(value, result.idf[token])

    def test_expected_tfidf_matches_pipeline(self) -> None:
        result = run_pipeline(TINY_DOCS)
        for name in result.documents:
            expected = read_token_weights(TINY_EXPECTED / "tfidf" / name)
            self.assertEqual(set(expected), set(result.tfidf[name]))
            for token, value in expected.items():
                self.assertAlmostEqual(value, result.tfidf[name][token])

    def test_writer_round_trip(self) -> None:
        result = run_pipeline(TINY_DOCS)
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            write_pipeline_tree(out, result.tf, result.df, result.idf, result.tfidf)
            rewritten, _dirty = read_idf(out / "idf.txt")
            self.assertAlmostEqual(rewritten["mice"], LN_3)
            self.assertTrue((out / "tfidf" / "cats.txt").exists())


if __name__ == "__main__":
    unittest.main()
