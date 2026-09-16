import unittest

from shelf_units.tokenize import tokenize, tokenize_perl, tokenize_perl_line


class TokenizeTests(unittest.TestCase):
    def test_lowercases_and_strips_punctuation(self):
        tokens = tokenize("Hello, White-Rabbit!")
        self.assertEqual(tokens, ["hello", "whiterabbit"])

    def test_keeps_digits(self):
        tokens = tokenize("Rule Forty-two. 42")
        self.assertEqual(tokens, ["rule", "fortytwo", "42"])

    def test_perl_line_counts_leading_empty_field(self):
        kept, count = tokenize_perl_line(" hello")
        self.assertEqual(kept, ["hello"])
        self.assertEqual(count, 2)

    def test_perl_line_strips_trailing_empty(self):
        kept, count = tokenize_perl_line("hello ")
        self.assertEqual(kept, ["hello"])
        self.assertEqual(count, 1)

    def test_perl_document_counts_sum_of_lines(self):
        tokens, count = tokenize_perl("Alpha\n beta\n")
        self.assertEqual(tokens, ["alpha", "beta"])
        self.assertEqual(count, 3)  # second line has a leading empty field


if __name__ == "__main__":
    unittest.main()
