import unittest

from textkit import truncate, word_count


class TestWordCount(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(word_count("hello brave world"), 3)

    def test_empty(self):
        self.assertEqual(word_count(""), 0)


class TruncateTests(unittest.TestCase):
    def test_short_text_unchanged(self):
        self.assertEqual(truncate("hi", 10), "hi")

    def test_exact_width_unchanged(self):
        self.assertEqual(truncate("hello", 5), "hello")

    def test_long_text_gets_ellipsis(self):
        self.assertEqual(truncate("hello world", 8), "hello w…")
        self.assertEqual(len(truncate("hello world", 8)), 8)

    def test_width_one_returns_ellipsis_only(self):
        self.assertEqual(truncate("hello", 1), "…")

    def test_non_positive_width_raises(self):
        for width in (0, -1):
            with self.subTest(width=width):
                with self.assertRaises(ValueError) as ctx:
                    truncate("hello", width)
                self.assertEqual(str(ctx.exception), "width must be positive")


if __name__ == "__main__":
    unittest.main()
