import unittest

from textkit import initials


class TestInitials(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(initials("ada lovelace"), "A.L.")

    def test_extra_whitespace(self):
        self.assertEqual(initials("  Grace   Brewster Murray  Hopper "), "G.B.M.H.")

    def test_empty(self):
        self.assertEqual(initials(""), "")

    def test_whitespace_only(self):
        self.assertEqual(initials("   "), "")

    def test_single_letter_words(self):
        self.assertEqual(initials("a b"), "A.B.")


if __name__ == "__main__":
    unittest.main()
