import unittest

from shelf_units.index import TfIdfIndex
from shelf_units.split_chapters import load_chapters


class ChapterSplitTests(unittest.TestCase):
    def test_alice_has_twelve_chapters(self):
        chapters = load_chapters("carroll-alice")
        self.assertEqual(len(chapters), 12)
        self.assertEqual(chapters[0].doc_id, "alice-i")
        self.assertIn("Rabbit-Hole", chapters[0].title)
        self.assertEqual(chapters[6].doc_id, "alice-vii")
        self.assertIn("hatter", chapters[6].text.lower())
        self.assertEqual(chapters[-1].doc_id, "alice-xii")
        self.assertIn("Evidence", chapters[-1].title)

    def test_alice_tea_query_lands_in_chapter_seven(self):
        index = TfIdfIndex(load_chapters("carroll-alice"))
        top, score = index.rank("mad hatter march hare tea", k=1)[0]
        self.assertEqual(top.doc_id, "alice-vii")
        self.assertGreater(score, 0.1)

    def test_milton_has_twelve_books(self):
        books = load_chapters("milton-paradise")
        self.assertEqual(len(books), 12)
        self.assertEqual(books[0].doc_id, "paradise-i")
        self.assertIn("disobedience", books[0].text.lower())
        self.assertEqual(books[-1].doc_id, "paradise-xii")

    def test_moby_has_front_matter_and_many_chapters(self):
        units = load_chapters("melville-moby_dick")
        ids = [doc.doc_id for doc in units]
        self.assertIn("moby-etymology", ids)
        self.assertIn("moby-extracts", ids)
        self.assertIn("moby-001", ids)
        self.assertGreaterEqual(len(units), 130)
        first_chapter = next(doc for doc in units if doc.doc_id == "moby-001")
        self.assertIn("Ishmael", first_chapter.text)

    def test_emma_has_roman_chapters(self):
        chapters = load_chapters("austen-emma")
        self.assertGreaterEqual(len(chapters), 40)
        self.assertTrue(chapters[0].doc_id.startswith("emma-"))
        self.assertIn("Woodhouse", chapters[0].text)


if __name__ == "__main__":
    unittest.main()
