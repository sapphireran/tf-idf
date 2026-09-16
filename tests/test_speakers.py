import unittest

from shelf_units.index import TfIdfIndex
from shelf_units.split_speakers import load_speakers


class SpeakerSplitTests(unittest.TestCase):
    def test_macbeth_voices_include_principals(self):
        voices = {doc.doc_id.split(":", 1)[1] for doc in load_speakers("shakespeare-macbeth")}
        for name in ("macbeth", "lady-macbeth", "macduff", "banquo", "witches"):
            self.assertIn(name, voices)

    def test_lady_macbeth_keeps_the_unsexing_line(self):
        docs = {doc.doc_id.split(":", 1)[1]: doc for doc in load_speakers("shakespeare-macbeth")}
        text = docs["lady-macbeth"].text.lower()
        # First Folio spelling.
        self.assertIn("vnsex", text)
        self.assertIn("spirits", text)

    def test_witches_keep_heath_vocabulary(self):
        docs = {doc.doc_id.split(":", 1)[1]: doc for doc in load_speakers("shakespeare-macbeth")}
        text = docs["witches"].text.lower()
        self.assertTrue("heath" in text or "raine" in text or "hurley" in text)

    def test_hamlet_query_prefers_hamlet_or_ghost(self):
        index = TfIdfIndex(load_speakers("shakespeare-hamlet"))
        ranked = [doc.doc_id for doc, _ in index.rank("horatio ghost denmark", k=3)]
        self.assertTrue(any(row.endswith(":hamlet") or row.endswith(":ghost") or row.endswith(":horatio") for row in ranked))

    def test_caesar_has_brutus_and_antony(self):
        voices = {doc.doc_id.split(":", 1)[1] for doc in load_speakers("shakespeare-caesar")}
        self.assertIn("brutus", voices)
        self.assertIn("antony", voices)
        self.assertIn("caesar", voices)


if __name__ == "__main__":
    unittest.main()
