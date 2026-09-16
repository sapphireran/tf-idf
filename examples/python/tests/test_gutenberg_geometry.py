"""Gutenberg-scale geometry: Folio plays cluster; unique casts do not."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

_EXAMPLES_PYTHON = Path(__file__).resolve().parents[1]
_REPO_ROOT = _EXAMPLES_PYTHON.parents[1]
if str(_EXAMPLES_PYTHON) not in sys.path:
    sys.path.insert(0, str(_EXAMPLES_PYTHON))

from similar_docs import cosine  # noqa: E402
from tfidf_toy import load_weight_table  # noqa: E402


TFIDF = _REPO_ROOT / "output" / "tfidf"


def _table(name: str) -> dict[str, float]:
    return load_weight_table(TFIDF / name)


class GutenbergGeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hamlet = _table("shakespeare-hamlet.txt")
        cls.macbeth = _table("shakespeare-macbeth.txt")
        cls.caesar = _table("shakespeare-caesar.txt")
        cls.emma = _table("austen-emma.txt")
        cls.sense = _table("austen-sense.txt")
        cls.persuasion = _table("austen-persuasion.txt")
        cls.alice = _table("carroll-alice.txt")
        cls.thursday = _table("chesterton-thursday.txt")
        cls.milton = _table("milton-paradise.txt")
        cls.bible = _table("bible-kjv.txt")

    def test_folio_plays_are_the_tightest_cluster(self) -> None:
        ham_mac = cosine(self.hamlet, self.macbeth)
        ham_cae = cosine(self.hamlet, self.caesar)
        mac_cae = cosine(self.macbeth, self.caesar)
        emma_sense = cosine(self.emma, self.sense)
        self.assertGreater(ham_mac, 0.25)
        self.assertGreater(ham_cae, 0.20)
        self.assertGreater(mac_cae, 0.18)
        self.assertGreater(ham_mac, emma_sense)

    def test_austen_cast_names_keep_novels_apart(self) -> None:
        emma_sense = cosine(self.emma, self.sense)
        emma_persuasion = cosine(self.emma, self.persuasion)
        self.assertLess(emma_sense, 0.12)
        self.assertLess(emma_persuasion, 0.15)
        self.assertGreater(emma_sense, 0.02)

    def test_alice_is_far_from_thursday_despite_shared_alice_token(self) -> None:
        # df(alice)=3, but Thursday only mentions the name; vectors stay apart.
        self.assertLess(cosine(self.alice, self.thursday), 0.05)

    def test_milton_shares_diction_with_the_bible(self) -> None:
        self.assertGreater(cosine(self.milton, self.bible), 0.15)


if __name__ == "__main__":
    unittest.main()
