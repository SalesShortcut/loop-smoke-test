import io
import json
import unittest

from textkit import core
from textkit.web import (
    MAX_BODY_BYTES,
    OPERATIONS,
    RESULT_PLACEHOLDER,
    TRUNCATE_WIDTH,
    PlaygroundHandler,
    handle_transform,
    list_transforms,
    port_from_env,
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

    def test_title_case_matches_core(self):
        self.assertEqual(transform("title_case", SAMPLE), core.title_case(SAMPLE))
        self.assertEqual(
            transform("title_case", SAMPLE), "Ada Lovelace Was a Mathematician"
        )

    def test_scenario_from_spec(self):
        self.assertEqual(transform("slugify", "Ada Lovelace"), "ada-lovelace")

    def test_supported_ops(self):
        self.assertEqual(
            sorted(OPERATIONS),
            [
                "initials",
                "reverse_words",
                "shout",
                "slugify",
                "title_case",
                "truncate",
            ],
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

    def test_missing_text_is_400(self):
        status, payload = handle_transform(self._body(op="shout"))
        self.assertEqual(status, 400)
        self.assertIn("error", payload)

    def test_missing_op_is_400(self):
        status, payload = handle_transform(self._body(text="hi"))
        self.assertEqual(status, 400)
        self.assertIn("error", payload)

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

    def test_fn_field_is_accepted(self):
        status, payload = handle_transform(
            self._body(fn="slugify", text="Ada Lovelace")
        )
        self.assertEqual((status, payload), (200, {"result": "ada-lovelace"}))

    def test_op_field_still_accepted(self):
        # The legacy alias: kept working on purpose (spec §1).
        status, payload = handle_transform(
            self._body(op="slugify", text="Ada Lovelace")
        )
        self.assertEqual((status, payload), (200, {"result": "ada-lovelace"}))

    def test_fn_wins_over_op(self):
        status, payload = handle_transform(
            self._body(fn="shout", op="slugify", text="hi")
        )
        self.assertEqual((status, payload), (200, {"result": "HI"}))

    def test_invalid_fn_is_not_rescued_by_op(self):
        # A caller who sends fn is never silently served by a stale op.
        status, payload = handle_transform(b'{"fn": 1, "op": "shout", "text": "x"}')
        self.assertEqual(status, 400)
        self.assertIn("error", payload)

    def test_missing_fn_is_400(self):
        status, payload = handle_transform(self._body(text="hi"))
        self.assertEqual(status, 400)
        self.assertIn("error", payload)

    def test_unknown_fn_is_400_with_error(self):
        status, payload = handle_transform(self._body(fn="nope", text=SAMPLE))
        self.assertEqual(status, 400)
        self.assertIn("nope", payload["error"])
        self.assertNotIn("result", payload)

    def test_non_string_fn_is_400(self):
        for payload_bytes in (
            b'{"fn": 1, "text": "x"}',
            b'{"fn": null, "text": "x"}',
            b'{"fn": ["shout"], "text": "x"}',
        ):
            with self.subTest(body=payload_bytes):
                status, payload = handle_transform(payload_bytes)
                self.assertEqual(status, 400)
                self.assertIn("error", payload)

    def test_missing_text_with_fn_is_400(self):
        status, payload = handle_transform(self._body(fn="shout"))
        self.assertEqual(status, 400)
        self.assertIn("error", payload)


class TestListTransforms(unittest.TestCase):
    def test_payload_shape(self):
        # The one literal pin of the published contract.
        self.assertEqual(
            list_transforms(),
            {
                "transforms": [
                    "initials",
                    "reverse_words",
                    "shout",
                    "slugify",
                    "title_case",
                    "truncate",
                ]
            },
        )

    def test_only_one_key(self):
        self.assertEqual(list(list_transforms()), ["transforms"])

    def test_derived_from_operations(self):
        self.assertEqual(list_transforms()["transforms"], sorted(OPERATIONS))

    def test_sorted(self):
        names = list_transforms()["transforms"]
        self.assertEqual(names, sorted(names))

    def test_every_listed_name_is_callable(self):
        for name in list_transforms()["transforms"]:
            with self.subTest(fn=name):
                body = json.dumps({"fn": name, "text": SAMPLE}).encode("utf-8")
                status, payload = handle_transform(body)
                self.assertEqual(status, 200)
                self.assertEqual(payload["result"], transform(name, SAMPLE))

    def test_word_count_is_not_exposed(self):
        # word_count takes one argument but returns an int, not text.
        self.assertNotIn("word_count", list_transforms()["transforms"])


def run_handler(method, path, headers=None, body=b""):
    """Drive PlaygroundHandler without a socket.

    Returns (status, headers, body_bytes, handler).
    """
    handler = PlaygroundHandler.__new__(PlaygroundHandler)
    handler.path = path
    handler.headers = headers or {}
    handler.rfile = io.BytesIO(body)
    handler.wfile = io.BytesIO()
    handler.request_version = "HTTP/1.1"
    handler.close_connection = False
    sent = {"status": None, "headers": {}}
    handler.send_response = lambda status: sent.__setitem__("status", status)
    handler.send_header = lambda name, value: sent["headers"].__setitem__(name, value)
    handler.end_headers = lambda: None
    getattr(handler, f"do_{method}")()
    return sent["status"], sent["headers"], handler.wfile.getvalue(), handler


class TestPlaygroundHandler(unittest.TestCase):
    def _post(self, body_bytes, path="/api/transform", headers=None):
        if headers is None:
            headers = {"Content-Length": str(len(body_bytes))}
        return run_handler("POST", path, headers, body_bytes)

    def test_get_root_serves_page(self):
        status, headers, body, _ = run_handler("GET", "/")
        self.assertEqual(status, 200)
        self.assertEqual(headers["Content-Type"], "text/html; charset=utf-8")
        self.assertIn(b"<title>textkit playground</title>", body)

    def test_get_root_with_query_string(self):
        status, _, _, _ = run_handler("GET", "/?utm_source=x")
        self.assertEqual(status, 200)

    def test_get_unknown_path_is_json_404(self):
        status, headers, body, _ = run_handler("GET", "/nope")
        self.assertEqual(status, 404)
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        self.assertEqual(json.loads(body), {"error": "not found"})

    def test_get_transforms_returns_json_list(self):
        status, headers, body, _ = run_handler("GET", "/api/transforms")
        self.assertEqual(status, 200)
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        self.assertEqual(json.loads(body), list_transforms())

    def test_get_transforms_with_query_string(self):
        status, _, body, _ = run_handler("GET", "/api/transforms?x=1")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), list_transforms())

    def test_get_transforms_trailing_slash_is_404(self):
        status, headers, body, _ = run_handler("GET", "/api/transforms/")
        self.assertEqual(status, 404)
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        self.assertEqual(json.loads(body), {"error": "not found"})

    def test_get_transform_singular_is_404(self):
        status, headers, body, _ = run_handler("GET", "/api/transform")
        self.assertEqual(status, 404)
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        self.assertEqual(json.loads(body), {"error": "not found"})

    def test_post_transforms_plural_is_404(self):
        payload = json.dumps({"fn": "shout", "text": "hi"}).encode()
        status, headers, body, _ = self._post(payload, path="/api/transforms")
        self.assertEqual(status, 404)
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        self.assertEqual(json.loads(body), {"error": "not found"})

    def test_post_transform_with_fn_ok(self):
        payload = json.dumps({"fn": "slugify", "text": "Ada Lovelace"}).encode()
        status, headers, body, _ = self._post(payload)
        self.assertEqual(status, 200)
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        self.assertEqual(json.loads(body), {"result": "ada-lovelace"})

    def test_post_transform_unknown_fn_is_400(self):
        payload = json.dumps({"fn": "nope", "text": "x"}).encode()
        status, _, body, _ = self._post(payload)
        self.assertEqual(status, 400)
        self.assertIsInstance(json.loads(body)["error"], str)

    def test_post_transform_ok(self):
        payload = json.dumps({"op": "slugify", "text": "Ada Lovelace"}).encode()
        status, headers, body, _ = self._post(payload)
        self.assertEqual(status, 200)
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        self.assertEqual(json.loads(body), {"result": "ada-lovelace"})

    def test_post_transform_with_query_string_routes(self):
        payload = json.dumps({"op": "shout", "text": "hi"}).encode()
        status, _, body, _ = self._post(payload, path="/api/transform?x=1")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), {"result": "HI"})

    def test_post_unknown_path_is_json_404(self):
        status, headers, body, _ = self._post(b"{}", path="/other")
        self.assertEqual(status, 404)
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        self.assertEqual(json.loads(body), {"error": "not found"})

    def test_post_without_content_length_is_400(self):
        status, _, body, _ = self._post(b"", headers={})
        self.assertEqual(status, 400)
        self.assertIn("error", json.loads(body))

    def test_post_non_numeric_content_length_is_400(self):
        status, _, body, _ = self._post(b"", headers={"Content-Length": "abc"})
        self.assertEqual(status, 400)
        self.assertIn("error", json.loads(body))

    def test_post_negative_content_length_is_400(self):
        status, _, body, _ = self._post(b"", headers={"Content-Length": "-5"})
        self.assertEqual(status, 400)
        self.assertIn("error", json.loads(body))

    def test_post_oversized_body_is_413(self):
        headers = {"Content-Length": str(MAX_BODY_BYTES + 1)}
        status, _, body, handler = self._post(b"", headers=headers)
        self.assertEqual(status, 413)
        self.assertIn("error", json.loads(body))
        self.assertTrue(handler.close_connection)

    def test_body_at_limit_is_not_rejected(self):
        text = "x" * (MAX_BODY_BYTES - 100)
        payload = json.dumps({"op": "shout", "text": text}).encode()
        self.assertLessEqual(len(payload), MAX_BODY_BYTES)
        status, _, _, _ = self._post(payload)
        self.assertEqual(status, 200)


class TestPortFromEnv(unittest.TestCase):
    def test_numeric_value(self):
        self.assertEqual(port_from_env("8080"), 8080)

    def test_unset_defaults(self):
        self.assertEqual(port_from_env(None), 3000)

    def test_empty_defaults(self):
        self.assertEqual(port_from_env(""), 3000)

    def test_invalid_value_exits_with_message(self):
        with self.assertRaises(SystemExit) as ctx:
            port_from_env("abc")
        self.assertIn("TEXTKIT_PORT", str(ctx.exception.code))


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
            '<button id="clear"',
            '<button id="title-case"',
            '<output id="result"',
            'id="charcount"',
            'id="footer"',
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.page)

    def test_charcount_starts_at_zero_below_the_textarea(self):
        # Live updating is exercised end-to-end; here we pin the markup contract.
        self.assertIn('<div id="charcount">0 characters</div>', self.page)
        self.assertLess(
            self.page.index('<textarea id="text"'),
            self.page.index('<div id="charcount">'),
        )

    def test_charcount_is_wired_to_input_and_clear(self):
        script = self.page[self.page.index("<script>"):]
        self.assertIn('getElementById("charcount")', script)
        self.assertIn('addEventListener("input"', script)
        self.assertIn(' + " characters"', script)
        # The clear handler must reset the counter to zero.
        clear_handler = script[script.index('getElementById("clear")'):]
        self.assertIn("showCount(0)", clear_handler)

    def test_result_starts_with_the_placeholder(self):
        # The only literal pin of the placeholder text; everything else
        # asserts against RESULT_PLACEHOLDER.
        self.assertEqual(
            RESULT_PLACEHOLDER, "Type something and press Apply Beza"
        )
        self.assertIn(
            f'<output id="result">{RESULT_PLACEHOLDER}</output>', self.page
        )

    def test_clear_restores_the_result_placeholder(self):
        # Clearing behavior itself is exercised end-to-end; here we pin the
        # markup contract: the handler writes the placeholder, not "".
        script = self.page[self.page.index("<script>"):]
        clear_handler = script[script.index('getElementById("clear")'):]
        self.assertIn(
            "getElementById(\"result\").textContent = "
            f"{json.dumps(RESULT_PLACEHOLDER)}",
            clear_handler,
        )

    def test_clear_button_is_labelled_and_wired(self):
        # Clearing behavior itself is exercised end-to-end in
        # e2e/tests/playground.spec.js; here we only pin the markup contract.
        self.assertIn('<button id="clear" type="button">Clear</button>', self.page)
        script = self.page[self.page.index("<script>"):]
        self.assertIn('getElementById("clear")', script)

    def test_title_case_button_is_labelled_and_wired(self):
        # The click behaviour is exercised end-to-end in
        # e2e/tests/title-case.spec.js; here we only pin the markup contract.
        self.assertIn(
            '<button id="title-case" type="button">Title Case</button>', self.page
        )
        script = self.page[self.page.index("<script>"):]
        self.assertIn('getElementById("title-case")', script)
        self.assertIn('"title_case"', script)
        # The button follows Clear in document order.
        self.assertLess(
            self.page.index('id="clear"'), self.page.index('id="title-case"')
        )

    def test_footer_counts_the_operations(self):
        # The literal count is pinned by the plan; test_supported_ops already
        # pins the operation set itself.
        self.assertIn(
            '<footer id="footer">textkit playground · 6 operations</footer>',
            self.page,
        )

    def test_footer_follows_the_result(self):
        self.assertLess(
            self.page.index('<output id="result"'),
            self.page.index('<footer id="footer">'),
        )

    def test_footer_is_static(self):
        # No script touches the footer: it never changes after load.
        script = self.page[self.page.index("<script>"):]
        self.assertNotIn('getElementById("footer")', script)

    def test_one_option_per_operation(self):
        for op in OPERATIONS:
            with self.subTest(op=op):
                self.assertIn(f'<option value="{op}">', self.page)

    def test_posts_to_the_api(self):
        self.assertIn("/api/transform", self.page)

    def test_page_posts_the_fn_field(self):
        # The page uses the canonical field name; `op` stays a legacy alias
        # covered by the request-level tests.
        script = self.page[self.page.index("<script>"):]
        body = script[script.index("JSON.stringify"):]
        self.assertIn("fn: op,", body)
        self.assertNotIn("op: op,", body)


if __name__ == "__main__":
    unittest.main()
