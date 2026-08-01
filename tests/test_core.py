import unittest

from textkit import (
    initials,
    reverse_words,
    shout,
    slugify,
    truncate,
    word_count,
)


class TestWordCount(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(word_count("hello brave world"), 3)

    def test_empty(self):
        self.assertEqual(word_count(""), 0)


class TestSlugify(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(slugify("Ada Lovelace"), "ada-lovelace")

    def test_punctuation_collapses(self):
        self.assertEqual(slugify("  Hello, World!!  "), "hello-world")

    def test_empty(self):
        self.assertEqual(slugify(""), "")


class TestShout(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(shout("ada lovelace"), "ADA LOVELACE")

    def test_empty(self):
        self.assertEqual(shout(""), "")


class TestInitials(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(initials("ada lovelace"), "A.L.")

    def test_extra_whitespace(self):
        self.assertEqual(initials("  grace   brewster  hopper "), "G.B.H.")

    def test_empty(self):
        self.assertEqual(initials(""), "")


class TestReverseWords(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(reverse_words("ada loved numbers"), "numbers loved ada")

    def test_empty(self):
        self.assertEqual(reverse_words(""), "")


class TestTruncate(unittest.TestCase):
    def test_shorter_than_width_is_unchanged(self):
        self.assertEqual(truncate("short", 20), "short")

    def test_exact_width_is_unchanged(self):
        self.assertEqual(truncate("12345", 5), "12345")

    def test_longer_text_is_cut(self):
        self.assertEqual(
            truncate("Ada Lovelace was a mathematician", 20),
            "Ada Lovelace was...",
        )

    def test_result_never_exceeds_width(self):
        self.assertLessEqual(len(truncate("x" * 100, 20)), 20)

    def test_tiny_width(self):
        self.assertEqual(truncate("abcdef", 2), "..")


if __name__ == "__main__":
    unittest.main()
