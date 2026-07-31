import unittest

from textkit import shout, word_count


class TestWordCount(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(word_count("hello brave world"), 3)

    def test_empty(self):
        self.assertEqual(word_count(""), 0)


class ShoutTests(unittest.TestCase):
    def test_uppercases_and_appends_bang(self):
        self.assertEqual(shout("hello"), "HELLO!")

    def test_existing_bang_not_duplicated(self):
        self.assertEqual(shout("stop!"), "STOP!")


if __name__ == "__main__":
    unittest.main()
