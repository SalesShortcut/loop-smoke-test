import unittest

from textkit import core
from textkit.web import OPERATIONS, TRUNCATE_WIDTH, transform

SAMPLE = "Ada Lovelace was a mathematician"


class TestTransform(unittest.TestCase):
    def test_slugify_matches_core(self):
        self.assertEqual(transform("slugify", SAMPLE), core.slugify(SAMPLE))

    def test_shout_matches_core(self):
        self.assertEqual(transform("shout", SAMPLE), core.shout(SAMPLE))

    def test_initials_matches_core(self):
        self.assertEqual(transform("initials", SAMPLE), core.initials(SAMPLE))

    def test_reverse_words_matches_core(self):
        self.assertEqual(
            transform("reverse_words", SAMPLE), core.reverse_words(SAMPLE)
        )

    def test_truncate_matches_core_at_playground_width(self):
        self.assertEqual(
            transform("truncate", SAMPLE), core.truncate(SAMPLE, TRUNCATE_WIDTH)
        )

    def test_truncate_width_is_20(self):
        self.assertEqual(TRUNCATE_WIDTH, 20)

    def test_scenario_from_spec(self):
        self.assertEqual(transform("slugify", "Ada Lovelace"), "ada-lovelace")

    def test_supported_ops(self):
        self.assertEqual(
            sorted(OPERATIONS),
            ["initials", "reverse_words", "shout", "slugify", "truncate"],
        )

    def test_unknown_op_raises(self):
        with self.assertRaises(ValueError):
            transform("nope", SAMPLE)

    def test_empty_op_raises(self):
        with self.assertRaises(ValueError):
            transform("", SAMPLE)


if __name__ == "__main__":
    unittest.main()
