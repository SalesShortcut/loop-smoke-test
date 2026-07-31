import unittest

from textkit import reverse_words, word_count


class TestWordCount(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(word_count("hello brave world"), 3)

    def test_empty(self):
        self.assertEqual(word_count(""), 0)


class ReverseWordsTests(unittest.TestCase):
    def test_reverses_word_order(self):
        self.assertEqual(reverse_words("a b c"), "c b a")


if __name__ == "__main__":
    unittest.main()
