import math
import unittest

from shelf_units.index import Document, TfIdfIndex
from shelf_units.weights import cosine, idf_classic, idf_smooth, tf_normalized, tfidf_classic


class WeightTests(unittest.TestCase):
    def test_normalized_tf(self):
        self.assertAlmostEqual(tf_normalized(2, 8), 0.25)

    def test_classic_idf_matches_snapshot_formula(self):
        # N = 18 files, df = 1 -> ln(18)
        self.assertAlmostEqual(idf_classic(18, 1), math.log(18))
        self.assertAlmostEqual(idf_classic(18, 18), 0.0)

    def test_smooth_idf_never_zero_for_corpus_wide_term(self):
        self.assertGreater(idf_smooth(18, 18), 0.0)

    def test_three_document_hand_example(self):
        # d1: cat cat cat milk
        # d2: dog dog milk
        # d3: bread bread
        cat = tfidf_classic(3, 4, 3, 1)
        milk_d1 = tfidf_classic(1, 4, 3, 2)
        dog = tfidf_classic(2, 3, 3, 1)
        bread = tfidf_classic(2, 2, 3, 1)
        self.assertAlmostEqual(cat, (3 / 4) * math.log(3 / 1))
        self.assertAlmostEqual(milk_d1, (1 / 4) * math.log(3 / 2))
        self.assertAlmostEqual(dog, (2 / 3) * math.log(3))
        self.assertAlmostEqual(bread, math.log(3))

    def test_index_agrees_with_hand_example(self):
        docs = [
            Document("d1", "cat", "cat cat cat milk"),
            Document("d2", "dog", "dog dog milk"),
            Document("d3", "bread", "bread bread"),
        ]
        index = TfIdfIndex(docs)
        self.assertAlmostEqual(index.vector("d1")["cat"], (3 / 4) * math.log(3))
        self.assertNotIn("milk", index.vector("d3"))
        # milk appears in 2 of 3 docs
        self.assertAlmostEqual(index.idf["milk"], math.log(3 / 2))

    def test_cosine_identical_vectors(self):
        vec = {"a": 0.4, "b": 0.3}
        self.assertAlmostEqual(cosine(vec, vec), 1.0)

    def test_rank_picks_the_obvious_document(self):
        docs = [
            Document("d1", "cat", "cat cat milk"),
            Document("d2", "dog", "dog dog milk"),
            Document("d3", "bread", "bread oven yeast"),
        ]
        index = TfIdfIndex(docs)
        top, score = index.rank("yeast bread", k=1)[0]
        self.assertEqual(top.doc_id, "d3")
        self.assertGreater(score, 0.5)


if __name__ == "__main__":
    unittest.main()
