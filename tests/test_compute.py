import math
import tempfile
import unittest
from pathlib import Path

from tfidf.compute import (
    build_index,
    build_index_from_documents,
    cosine_sparse,
    idf_value,
    score_query,
)
from tfidf.io_tsv import read_weight_table, write_pipeline_output
from tfidf.report import render_corpus_report


class IdfTests(unittest.TestCase):
    def test_raw_idf_is_natural_log_of_n_over_df(self):
        self.assertAlmostEqual(idf_value(18, 1, "raw"), math.log(18))
        self.assertAlmostEqual(idf_value(18, 18, "raw"), 0.0)

    def test_smooth_idf_stays_positive_when_term_is_everywhere(self):
        value = idf_value(18, 18, "smooth")
        self.assertGreater(value, 1.0)
        self.assertAlmostEqual(value, math.log(19 / 19) + 1.0)


class HandCalculationTests(unittest.TestCase):
    """Three six-token documents; every number is checked against log(N/df)."""

    @staticmethod
    def _index():
        docs = [
            ("doc-a.txt", ["the", "cat", "sat", "on", "the", "mat"], 6),
            ("doc-b.txt", ["the", "dog", "sat", "on", "the", "log"], 6),
            ("doc-c.txt", ["a", "cat", "and", "a", "dog", "played"], 6),
        ]
        return build_index_from_documents(docs, idf_mode="raw")

    def test_document_frequency(self):
        index = self._index()
        self.assertEqual(index.n_documents, 3)
        self.assertEqual(index.df["the"], 2)
        self.assertEqual(index.df["cat"], 2)
        self.assertEqual(index.df["mat"], 1)
        self.assertEqual(index.df["played"], 1)

    def test_tf_is_count_over_length(self):
        doc_a = self._index().document("doc-a.txt")
        self.assertAlmostEqual(doc_a.tf["the"], 2 / 6)
        self.assertAlmostEqual(doc_a.tf["mat"], 1 / 6)

    def test_tfidf_matches_hand_arithmetic(self):
        index = self._index()
        doc_a = index.document("doc-a.txt")
        expected_mat = (1 / 6) * math.log(3 / 1)
        expected_the = (2 / 6) * math.log(3 / 2)
        self.assertAlmostEqual(doc_a.tfidf["mat"], expected_mat)
        self.assertAlmostEqual(doc_a.tfidf["the"], expected_the)
        self.assertGreater(doc_a.tfidf["mat"], doc_a.tfidf["the"])
        self.assertEqual(doc_a.top_terms(1), [("mat", doc_a.tfidf["mat"])])

    def test_query_prefers_the_matching_document(self):
        index = self._index()
        ranked = score_query(index, "the mat")
        self.assertEqual(ranked[0][0], "doc-a.txt")
        self.assertGreater(ranked[0][1], ranked[1][1])


class TinyCorpusTests(unittest.TestCase):
    CORPUS = Path(__file__).resolve().parents[1] / "examples" / "tiny-corpus"

    def test_distinctive_headwords_win(self):
        index = build_index(self.CORPUS)
        winners = {
            "cats.txt": "miso",
            "sourdough.txt": "levain",
            "harbor.txt": "jib",
            "jupiter.txt": "ganymede",
        }
        for name, expected in winners.items():
            top = [term for term, _score in index.top_terms(name, n=8)]
            self.assertIn(
                expected,
                top,
                f"{expected!r} should rank in the top 8 of {name}, got {top}",
            )

    def test_shared_function_words_are_not_the_top_hit(self):
        index = build_index(self.CORPUS)
        for doc in index.documents:
            top_term, _score = doc.top_terms(1)[0]
            self.assertNotIn(top_term, {"the", "a", "and", "of", "to", "in"})

    def test_jupiter_query_ranks_jupiter_first(self):
        index = build_index(self.CORPUS)
        ranked = score_query(index, "ganymede telescope opposition")
        self.assertEqual(ranked[0][0], "jupiter.txt")

    def test_sourdough_query_ranks_sourdough_first(self):
        index = build_index(self.CORPUS)
        ranked = score_query(index, "levain gluten dutch oven crumb")
        self.assertEqual(ranked[0][0], "sourdough.txt")


class PipelineIoTests(unittest.TestCase):
    def test_round_trip_tsv(self):
        docs = [
            ("short.txt", ["alpha", "beta"], 2),
            ("other.txt", ["alpha", "gamma"], 2),
        ]
        index = build_index_from_documents(docs)
        with tempfile.TemporaryDirectory() as tmp:
            root = write_pipeline_output(index, tmp)
            idf = read_weight_table(root / "idf.txt")
            tfidf = read_weight_table(root / "tfidf" / "short.txt")
        self.assertAlmostEqual(idf["beta"], math.log(2 / 1))
        self.assertAlmostEqual(tfidf["beta"], (1 / 2) * math.log(2 / 1))
        self.assertAlmostEqual(idf["alpha"], 0.0)
        self.assertEqual(tfidf["alpha"], 0.0)

    def test_report_mentions_every_document(self):
        docs = [
            ("one.txt", ["rare", "word"], 2),
            ("two.txt", ["other", "word"], 2),
        ]
        report = render_corpus_report(build_index_from_documents(docs), top_n=3)
        self.assertIn("one.txt", report)
        self.assertIn("two.txt", report)
        self.assertIn("rare", report)


class CosineTests(unittest.TestCase):
    def test_identical_vectors(self):
        self.assertAlmostEqual(cosine_sparse({"a": 3.0}, {"a": 3.0}), 1.0)

    def test_orthogonal_vectors(self):
        self.assertEqual(cosine_sparse({"a": 1.0}, {"b": 1.0}), 0.0)

    def test_empty_is_zero(self):
        self.assertEqual(cosine_sparse({}, {"a": 1.0}), 0.0)


if __name__ == "__main__":
    unittest.main()
