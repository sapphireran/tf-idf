import math
import unittest
from pathlib import Path

from tfidf.compute import build_index


HAND = Path(__file__).resolve().parents[1] / "examples" / "hand-calculation" / "corpus"


class HandCorpusFileTests(unittest.TestCase):
    def test_files_reproduce_the_worked_example(self):
        index = build_index(HAND)
        self.assertEqual(index.n_documents, 3)
        doc_a = index.document("doc-a.txt")
        self.assertEqual(doc_a.token_count, 6)
        self.assertAlmostEqual(doc_a.tfidf["mat"], (1 / 6) * math.log(3))
        self.assertEqual(doc_a.top_terms(1)[0][0], "mat")
        self.assertEqual(index.document("doc-b.txt").top_terms(1)[0][0], "log")
        # "a" occurs twice in C and nowhere else, so it outranks "played".
        # TF-IDF has no stopword list; repeated unique tokens win on TF.
        self.assertEqual(index.document("doc-c.txt").top_terms(1)[0][0], "a")
