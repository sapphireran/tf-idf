import unittest

from tfidf.tokenize import normalize_text, tokenize, tokenize_document, tokenize_line


class TokenizeTests(unittest.TestCase):
    def test_lowercase_and_strip_punctuation(self):
        self.assertEqual(tokenize("Hello, World!"), ["hello", "world"])

    def test_apostrophes_are_removed_not_split(self):
        # Same as the Perl s/[^a-zA-Z\\d\\s]//g rule: "it's" -> "its"
        self.assertEqual(tokenize("it's a cat"), ["its", "a", "cat"])

    def test_digits_are_kept(self):
        self.assertEqual(tokenize("Room 221B"), ["room", "221b"])

    def test_hyphenated_words_collapse(self):
        self.assertEqual(tokenize("sperm-whale"), ["spermwhale"])

    def test_normalize_collapses_whitespace(self):
        self.assertEqual(normalize_text("a\t\tb\n c"), "a b c")

    def test_default_line_ignores_leading_space_in_denominator(self):
        tokens, denom = tokenize_line("  cat sat")
        self.assertEqual(tokens, ["cat", "sat"])
        self.assertEqual(denom, 2)

    def test_perl_compat_counts_leading_empty_field(self):
        tokens, denom = tokenize_line("  cat sat", perl_compat=True)
        self.assertEqual(tokens, ["cat", "sat"])
        self.assertEqual(denom, 3)

    def test_perl_compat_drops_trailing_empty_like_perl_split(self):
        tokens, denom = tokenize_line("cat sat  ", perl_compat=True)
        self.assertEqual(tokens, ["cat", "sat"])
        self.assertEqual(denom, 2)

    def test_tokenize_document_from_raw_string(self):
        tokens, denom = tokenize_document("the cat\nsat on the mat")
        self.assertEqual(tokens, ["the", "cat", "sat", "on", "the", "mat"])
        self.assertEqual(denom, 6)


if __name__ == "__main__":
    unittest.main()
