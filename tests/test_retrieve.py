import unittest

from shelf_units.retrieve import rank_passages, window_passages
from shelf_units.split_chapters import load_chapters


class RetrieveTests(unittest.TestCase):
    def test_windows_cover_the_token_stream(self):
        text = " ".join(f"w{i}" for i in range(25))
        docs = window_passages(text, source="toy", window=10, stride=10, prefix="t")
        self.assertEqual(len(docs), 3)
        self.assertEqual(docs[0].doc_id, "t-0000")
        self.assertTrue(docs[-1].text.startswith("w20") or "w24" in docs[-1].text)

    def test_alice_passage_finds_the_tea_party(self):
        alice = "\n\n".join(doc.text for doc in load_chapters("carroll-alice"))
        rows = rank_passages(
            alice,
            "hatter march hare tea twinkle",
            source="alice",
            window=60,
            stride=30,
            k=5,
        )
        self.assertGreaterEqual(len(rows), 1)
        blob = " ".join(passage.text for passage, _ in rows)
        self.assertTrue("hatter" in blob or "hare" in blob)

    def test_rejects_bad_window(self):
        with self.assertRaises(ValueError):
            window_passages("hello", source="x", window=0, stride=10)


if __name__ == "__main__":
    unittest.main()
