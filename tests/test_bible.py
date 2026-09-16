import unittest

from shelf_units.index import TfIdfIndex
from shelf_units.split_bible import expected_book_ids, load_bible


class BibleSplitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.books = load_bible()
        cls.by_id = {doc.doc_id: doc for doc in cls.books}

    def test_expected_unit_count_and_order(self):
        expected = expected_book_ids()
        self.assertEqual([doc.doc_id for doc in self.books], expected)
        self.assertEqual(len(self.books), 55)

    def test_genesis_opens_at_creation(self):
        self.assertIn("In the beginning God created", self.by_id["genesis"].text)

    def test_exodus_is_not_still_genesis(self):
        self.assertIn("Now these are the names of the children of Israel", self.by_id["exodus"].text)
        self.assertNotIn("In the beginning God created", self.by_id["exodus"].text)

    def test_samuel_alias_line_does_not_become_kings(self):
        # 1 Samuel's "Otherwise Called: The First Book of the Kings" must stay
        # inside Samuel, not open 1 Kings early.
        self.assertIn("Ramathaimzophim", self.by_id["1-samuel"].text)
        self.assertIn("king David was old and stricken", self.by_id["1-kings"].text)
        self.assertNotIn("Ramathaimzophim", self.by_id["1-kings"].text)

    def test_second_kings_starts_with_moab(self):
        self.assertIn("Then Moab rebelled against Israel", self.by_id["2-kings"].text)

    def test_ezra_is_not_a_genealogy_false_positive(self):
        self.assertIn("first year of Cyrus king of Persia", self.by_id["ezra"].text)

    def test_hosea_malachi_holds_the_untitled_prophets(self):
        blob = self.by_id["hosea-malachi"].text
        self.assertIn("Nineveh", blob)
        self.assertIn("Elijah the prophet", blob)
        self.assertNotIn("In the beginning God created", blob)
        self.assertNotIn("generation of Jesus Christ", blob)

    def test_matthew_and_revelation_bookend_the_new_testament(self):
        self.assertIn("generation of Jesus Christ", self.by_id["matthew"].text)
        self.assertIn("The Revelation of Jesus Christ", self.by_id["revelation"].text)

    def test_query_elects_the_obvious_book(self):
        index = TfIdfIndex(self.books)
        top, _ = index.rank("pharaoh egypt passover", k=1)[0]
        self.assertEqual(top.doc_id, "exodus")
        top, _ = index.rank("nineveh great fish jonah", k=1)[0]
        self.assertEqual(top.doc_id, "hosea-malachi")
        top, _ = index.rank("laban rachel rebekah esau", k=1)[0]
        self.assertEqual(top.doc_id, "genesis")


if __name__ == "__main__":
    unittest.main()
