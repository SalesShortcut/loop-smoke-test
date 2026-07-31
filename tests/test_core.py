import unittest

import textkit
from textkit import reverse_words, word_count


class TestWordCount(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(word_count("hello brave world"), 3)

    def test_empty(self):
        self.assertEqual(word_count(""), 0)


class ReverseWordsTests(unittest.TestCase):
    def test_reverses_word_order(self):
        self.assertEqual(reverse_words("a b c"), "c b a")

    def test_collapses_surrounding_and_repeated_spaces(self):
        self.assertEqual(reverse_words("  a   b "), "b a")

    def test_empty_string(self):
        self.assertEqual(reverse_words(""), "")

    def test_whitespace_only_string(self):
        self.assertEqual(reverse_words("   "), "")

    def test_exported_from_package(self):
        self.assertIn("reverse_words", textkit.__all__)


if __name__ == "__main__":
    unittest.main()
