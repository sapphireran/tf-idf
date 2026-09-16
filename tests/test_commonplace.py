import unittest

from shelf_units.commonplace import load_commonplace
from shelf_units.index import TfIdfIndex


QUERIES = [
    ("hypo fixer enlarger dektol", "01-darkroom"),
    ("anemones limpets holdfasts urchins kelp chiton", "02-tide-pool"),
    ("terminus fluorescent validator night bus", "03-night-bus"),
    ("zugzwang lucena philidor opposition", "04-endgame-study"),
    ("nib tines converter babybottom", "05-fountain-pen"),
    ("afterdrop neoprene jetty cold shock", "06-winter-swim"),
    ("centering grog leatherhard splash", "07-pottery-wheel"),
    ("channeling portafilter blonding wdt puck", "08-espresso-dial"),
    ("averted messier collimation declination", "09-star-chart"),
    ("platen escapement pica typebar", "10-typewriter-ribbon"),
    ("queenright varroa brood smoker", "11-beekeeping"),
    ("attack point reentrant control flag", "12-orienteering"),
]


class CommonplaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.notes = load_commonplace()
        cls.index = TfIdfIndex(cls.notes)

    def test_twelve_notes(self):
        self.assertEqual(len(self.notes), 12)

    def test_each_seeded_query_elects_its_note(self):
        for query, expected in QUERIES:
            with self.subTest(query=query):
                top, score = self.index.rank(query, k=1)[0]
                self.assertEqual(top.doc_id, expected)
                self.assertGreater(score, 0.15)

    def test_darkroom_top_terms_are_photographic(self):
        terms = {term for term, _ in self.index.top_terms("01-darkroom", k=10)}
        self.assertTrue(terms & {"enlarger", "fixer", "hypo", "dektol", "dodge", "grain"})


if __name__ == "__main__":
    unittest.main()
