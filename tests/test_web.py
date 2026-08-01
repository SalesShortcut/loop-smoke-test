import json
import unittest

from textkit import core
from textkit.web import (
    OPERATIONS,
    TRUNCATE_WIDTH,
    handle_transform,
    render_page,
    transform,
)

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


class TestHandleTransform(unittest.TestCase):
    def _body(self, **payload) -> bytes:
        return json.dumps(payload).encode("utf-8")

    def test_ok_response(self):
        status, payload = handle_transform(
            self._body(op="slugify", text="Ada Lovelace")
        )
        self.assertEqual((status, payload), (200, {"result": "ada-lovelace"}))

    def test_every_op_returns_200(self):
        for op in OPERATIONS:
            with self.subTest(op=op):
                status, payload = handle_transform(self._body(op=op, text=SAMPLE))
                self.assertEqual(status, 200)
                self.assertEqual(payload["result"], transform(op, SAMPLE))

    def test_missing_text_defaults_to_empty(self):
        self.assertEqual(handle_transform(self._body(op="shout")), (200, {"result": ""}))

    def test_unknown_op_is_400_with_error(self):
        status, payload = handle_transform(self._body(op="nope", text=SAMPLE))
        self.assertEqual(status, 400)
        self.assertIn("nope", payload["error"])
        self.assertNotIn("result", payload)

    def test_malformed_json_is_400(self):
        status, payload = handle_transform(b"{not json")
        self.assertEqual(status, 400)
        self.assertIn("error", payload)

    def test_empty_body_is_400(self):
        status, payload = handle_transform(b"")
        self.assertEqual(status, 400)
        self.assertIn("error", payload)

    def test_non_object_body_is_400(self):
        status, payload = handle_transform(b"[1, 2, 3]")
        self.assertEqual(status, 400)
        self.assertIn("error", payload)

    def test_non_string_fields_are_400(self):
        for payload_bytes in (b'{"op": 1, "text": "x"}', b'{"op": "shout", "text": 1}'):
            with self.subTest(body=payload_bytes):
                status, payload = handle_transform(payload_bytes)
                self.assertEqual(status, 400)
                self.assertIn("error", payload)


class TestRenderPage(unittest.TestCase):
    def setUp(self):
        self.page = render_page()

    def test_title(self):
        self.assertIn("<title>textkit playground</title>", self.page)

    def test_required_elements(self):
        for fragment in (
            '<textarea id="text"',
            '<select id="op"',
            '<button id="apply"',
            '<output id="result"',
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.page)

    def test_one_option_per_operation(self):
        for op in OPERATIONS:
            with self.subTest(op=op):
                self.assertIn(f'<option value="{op}">', self.page)

    def test_posts_to_the_api(self):
        self.assertIn("/api/transform", self.page)


if __name__ == "__main__":
    unittest.main()
