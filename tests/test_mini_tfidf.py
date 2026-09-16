"""Lock the hand-worked three-document example and a few Gutenberg facts."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
sys.path.insert(0, str(EXAMPLES))

from cosine_similarity import load_output_vectors, pairs_from_vectors  # noqa: E402
from follow_word import main as follow_main  # noqa: E402
from mini_tfidf import main as mini_main, modes_for_variant  # noqa: E402
from rank_terms import main as rank_main  # noqa: E402
from tfidf_lib import (  # noqa: E402
    build_model,
    cosine,
    pairwise_cosine,
    parse_tsv_scores,
    rank_score_map,
    read_documents,
    tokenize,
)


THREE_DOCS = EXAMPLES / "mini_corpus" / "three_docs"
SNIPPETS = EXAMPLES / "mini_corpus" / "literary_snippets"
LN3 = math.log(3)
LN_3_2 = math.log(3 / 2)


class TokenizerTests(unittest.TestCase):
    def test_lowercases_and_drops_punctuation(self) -> None:
        self.assertEqual(tokenize("Alice's rabbit."), ["alices", "rabbit"])

    def test_collapses_whitespace_and_skips_empty(self) -> None:
        self.assertEqual(tokenize("  the   whale\nswims  "), ["the", "whale", "swims"])

    def test_keeps_digits(self) -> None:
        self.assertEqual(tokenize("Chapter 1: Down"), ["chapter", "1", "down"])


class ThreeDocsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.model = build_model(read_documents(THREE_DOCS))

    def test_counts_three_documents_and_nine_terms(self) -> None:
        self.assertEqual(self.model.n_docs, 3)
        self.assertEqual(
            self.model.vocabulary,
            ["a", "bird", "harbor", "in", "sings", "song", "swims", "the", "whale"],
        )

    def test_idf_matches_hand_calculation(self) -> None:
        self.assertEqual(self.model.df["the"], 3)
        self.assertEqual(self.model.idf["the"], 0.0)
        self.assertAlmostEqual(self.model.idf["whale"], LN_3_2)
        self.assertAlmostEqual(self.model.idf["bird"], LN3)
        self.assertAlmostEqual(self.model.idf["harbor"], LN3)

    def test_harbor_tfidf(self) -> None:
        harbor = self.model.tfidf["the_harbor.txt"]
        self.assertEqual(harbor["the"], 0.0)
        self.assertAlmostEqual(harbor["whale"], (1 / 6) * LN_3_2)
        self.assertAlmostEqual(harbor["swims"], (1 / 6) * LN3)
        self.assertAlmostEqual(harbor["in"], (1 / 6) * LN3)
        self.assertAlmostEqual(harbor["harbor"], (1 / 6) * LN3)

    def test_song_and_bird_products(self) -> None:
        song = self.model.tfidf["the_song.txt"]
        bird = self.model.tfidf["the_bird.txt"]
        shared = 0.2 * LN_3_2
        self.assertAlmostEqual(song["whale"], shared)
        self.assertAlmostEqual(song["sings"], shared)
        self.assertAlmostEqual(bird["sings"], shared)
        self.assertAlmostEqual(bird["bird"], 0.2 * LN3)
        self.assertGreater(bird["bird"], shared)

    def test_rankings(self) -> None:
        harbor_top = [term for term, _ in self.model.ranked("the_harbor.txt")]
        self.assertEqual(set(harbor_top[:3]), {"swims", "in", "harbor"})
        self.assertEqual(harbor_top[-1], "the")
        bird_top = [term for term, _ in self.model.ranked("the_bird.txt")]
        self.assertEqual(bird_top[0], "bird")
        self.assertEqual(bird_top[-1], "the")

    def test_cosine_order(self) -> None:
        pairs = {(left, right): score for left, right, score in pairwise_cosine(self.model)}
        close = pairs[("the_bird.txt", "the_song.txt")]
        mid = pairs[("the_harbor.txt", "the_song.txt")]
        far = pairs[("the_harbor.txt", "the_bird.txt")]
        self.assertGreater(close, mid)
        self.assertGreater(mid, far)
        self.assertGreater(mid, 0.0)
        self.assertEqual(far, 0.0)

    def test_cli_exits_zero(self) -> None:
        self.assertEqual(mini_main([str(THREE_DOCS), "--top", "5"]), 0)


class VariantTests(unittest.TestCase):
    def test_smooth_idf_makes_the_nonzero(self) -> None:
        tf_mode, idf_mode = modes_for_variant("smooth")
        model = build_model(read_documents(THREE_DOCS), tf_mode=tf_mode, idf_mode=idf_mode)
        self.assertAlmostEqual(model.idf["the"], 1.0)
        self.assertGreater(model.tfidf["the_harbor.txt"]["the"], 0.0)

    def test_log_tf_does_not_divide_by_length(self) -> None:
        tf_mode, idf_mode = modes_for_variant("log_tf")
        model = build_model(read_documents(THREE_DOCS), tf_mode=tf_mode, idf_mode=idf_mode)
        # one occurrence → 1 + ln(1) = 1, times idf(whale)
        self.assertAlmostEqual(model.tf["the_harbor.txt"]["whale"], 1.0)
        self.assertAlmostEqual(model.tfidf["the_harbor.txt"]["whale"], LN_3_2)


class SnippetTests(unittest.TestCase):
    def test_expected_names_rank_first(self) -> None:
        model = build_model(read_documents(SNIPPETS))
        self.assertEqual(model.ranked("alice.txt")[0][0], "alice")
        ishmael_terms = [term for term, _ in model.ranked("ishmael.txt")[:6]]
        self.assertTrue({"ishmael", "whale"} & set(ishmael_terms))
        hamlet_terms = [term for term, score in model.ranked("hamlet.txt") if score > 0]
        self.assertIn("question", hamlet_terms)


class GutenbergTableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.idf = parse_tsv_scores(ROOT / "output" / "idf.txt")
        cls.alice = parse_tsv_scores(ROOT / "output" / "tfidf" / "carroll-alice.txt")
        cls.alice_tf = parse_tsv_scores(ROOT / "output" / "tf" / "carroll-alice.txt")

    def test_the_is_exactly_zero(self) -> None:
        self.assertEqual(self.idf["the"], 0.0)
        self.assertEqual(self.idf["a"], 0.0)
        self.assertEqual(self.alice["the"], 0.0)

    def test_alice_idf_is_ln_18_over_3(self) -> None:
        self.assertAlmostEqual(self.idf["alice"], math.log(18 / 3), places=12)

    def test_unique_terms_use_ln_18(self) -> None:
        self.assertAlmostEqual(self.idf["moby"], math.log(18), places=12)
        self.assertAlmostEqual(self.idf["macbeth"], math.log(18), places=12)

    def test_alice_product_matches_tf_times_idf(self) -> None:
        self.assertAlmostEqual(
            self.alice["alice"],
            self.alice_tf["alice"] * self.idf["alice"],
            places=12,
        )

    def test_alice_is_the_top_term(self) -> None:
        self.assertEqual(rank_score_map(self.alice, top=1)[0][0], "alice")

    def test_rank_and_follow_clis(self) -> None:
        self.assertEqual(
            rank_main(["--input-dir", str(ROOT / "output" / "tfidf"), "--only", "carroll-alice.txt", "--top", "5"]),
            0,
        )
        self.assertEqual(follow_main(["alice", "--output-dir", str(ROOT / "output")]), 0)

    def test_gutenberg_cosine_clusters_austen(self) -> None:
        names, vectors = load_output_vectors(ROOT / "output" / "tfidf")
        pairs = {(left, right): score for left, right, score in pairs_from_vectors(names, vectors)}
        austen = pairs[("austen-emma.txt", "austen-sense.txt")]
        mixed = pairs[("austen-emma.txt", "melville-moby_dick.txt")]
        self.assertGreater(austen, mixed)


class CosineUnitTests(unittest.TestCase):
    def test_identical_and_orthogonal(self) -> None:
        self.assertAlmostEqual(cosine([1.0, 0.0], [1.0, 0.0]), 1.0)
        self.assertEqual(cosine([1.0, 0.0], [0.0, 2.0]), 0.0)
        self.assertEqual(cosine([0.0, 0.0], [1.0, 1.0]), 0.0)


if __name__ == "__main__":
    unittest.main()
