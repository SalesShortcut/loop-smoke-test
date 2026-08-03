import unittest

from textkit import (
    initials,
    reverse_words,
    shout,
    slugify,
    title_case,
    truncate,
    word_count,
)
from textkit.core import TITLE_CASE_CONNECTORS


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

    def test_diacritics_reduce_to_ascii(self):
        self.assertEqual(slugify("Café au lait"), "cafe-au-lait")

    def test_non_latin_scripts_are_dropped(self):
        self.assertEqual(slugify("Привет"), "")
        self.assertEqual(slugify("Привет ada"), "ada")


class TestShout(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(shout("ada lovelace"), "ADA LOVELACE")

    def test_empty(self):
        self.assertEqual(shout(""), "")


class TestTitleCase(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(title_case(""), "")

    def test_single_word(self):
        self.assertEqual(title_case("ada"), "Ada")

    def test_connector_word_first(self):
        self.assertEqual(title_case("the analytical engine"), "The Analytical Engine")

    def test_connectors_stay_lowercase(self):
        self.assertEqual(
            title_case("ada lovelace and the analytical engine"),
            "Ada Lovelace and the Analytical Engine",
        )

    def test_all_caps_input_is_normalised(self):
        self.assertEqual(title_case("ADA LOVELACE"), "Ada Lovelace")

    def test_every_connector_is_lowercased(self):
        for word in TITLE_CASE_CONNECTORS:
            with self.subTest(word=word):
                self.assertEqual(title_case(f"start {word} end"), f"Start {word} End")

    def test_extra_whitespace_collapses(self):
        self.assertEqual(
            title_case("  grace   brewster  hopper "), "Grace Brewster Hopper"
        )

    def test_scenario_from_spec(self):
        self.assertEqual(title_case("a tale of two cities"), "A Tale of Two Cities")


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
