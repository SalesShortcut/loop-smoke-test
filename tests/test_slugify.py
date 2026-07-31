import unittest

from textkit import slugify


class TestSlugify(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(slugify("Hello, World!"), "hello-world")

    def test_digits(self):
        self.assertEqual(slugify("Python 3.12 rocks"), "python-3-12-rocks")

    def test_empty(self):
        self.assertEqual(slugify(""), "")

    def test_cyrillic_only(self):
        self.assertEqual(slugify("  Много   пробелов  "), "")

    def test_strips_dashes(self):
        self.assertEqual(slugify("---hello---"), "hello")
        self.assertEqual(slugify("  spaced out  "), "spaced-out")

    def test_collapses_separators(self):
        self.assertEqual(slugify("a --- b ... c"), "a-b-c")

    def test_only_punctuation(self):
        self.assertEqual(slugify("!!!???"), "")

    def test_allowed_chars_only(self):
        self.assertEqual(slugify("Über Straße 42"), "ber-stra-e-42")


if __name__ == "__main__":
    unittest.main()
