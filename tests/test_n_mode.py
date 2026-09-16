"""N-mode: gold uses 18 texts; Perl $#files does not."""

from __future__ import annotations

import unittest
from pathlib import Path

from querydesk.index import collection_size
from querydesk.tokenize import perl_last_index_n

ROOT = Path(__file__).resolve().parent.parent


class NModeTests(unittest.TestCase):
    def test_gutenberg_text_count_is_eighteen(self) -> None:
        self.assertEqual(collection_size(ROOT / "gutenberg", "texts"), 18)

    def test_perl_last_index_counts_dot_entries(self) -> None:
        gutenberg = ROOT / "gutenberg"
        self.assertEqual(perl_last_index_n(gutenberg), collection_size(gutenberg, "perl-last-index"))
        self.assertGreater(perl_last_index_n(gutenberg), 18)

    def test_field_notes_n_matches_file_count(self) -> None:
        notes = ROOT / "examples" / "field-notes" / "texts"
        self.assertEqual(collection_size(notes, "texts"), 4)
