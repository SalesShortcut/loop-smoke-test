# JSON transform API — implementation plan

Spec: `docs/superpowers/specs/issue-19-design.md`
(source of truth; its Locked decisions are binding).
Issue: #19

Do the tasks in order; each one leaves `python3 -m unittest discover -s tests -v`
green. Everything lands in a **single commit** at Task 6, message prefixed
`[textkit] ` per `CLAUDE.md` — e.g.
`[textkit] feat: JSON transform API (GET /api/transforms, fn field)`.

Baseline before starting: 75 tests, green.

## Task 1: accept `fn` on `POST /api/transform`

File: `textkit/web.py`, function `handle_transform`.

- [ ] Replace the two lines that read `op` / `text` from the payload with the
  aliasing lookup from the spec (§1):

  ```python
  name = payload["fn"] if "fn" in payload else payload.get("op")
  text = payload.get("text")
  if not isinstance(name, str):
      return 400, {"error": '"fn" must be a string'}
  if not isinstance(text, str):
      return 400, {"error": '"text" must be a string'}
  ```

  Use `"fn" in payload` — **not** `payload.get("fn") or payload.get("op")` —
  so `{"fn": 1, "op": "shout"}` is a 400 rather than silently running `shout`.
- [ ] Pass `name` to `transform(...)`. Do **not** rename `transform`'s
  parameter or change its `ValueError` message (`unknown op: ...`); its
  doctest pins that text and `tests/test_web.py` pins the behaviour.
- [ ] Update the `handle_transform` docstring: the `Example:` call becomes
  `handle_transform(b'{"fn": "shout", "text": "hi"}')` → `(200, {'result': 'HI'})`,
  and one prose sentence records that `op` is accepted as a legacy alias and
  that `fn` wins when both are present.
- [ ] Verify by hand that nothing else in the module reads `payload["op"]`.

## Task 2: `GET /api/transforms`

File: `textkit/web.py`.

- [ ] Add `list_transforms() -> dict` next to `handle_transform` (after it,
  before `render_page`):

  ```python
  def list_transforms() -> dict:
      """Return the payload for GET /api/transforms.

      Example:
          >>> list_transforms()["transforms"][:2]
          ['initials', 'reverse_words']
      """
      return {"transforms": sorted(OPERATIONS)}
  ```

  The `Example:` section is mandatory per `CLAUDE.md`. Keep the body derived
  from `OPERATIONS` — never a literal list.
- [ ] In `PlaygroundHandler.do_GET`, replace the single `!= "/"` guard with an
  explicit route on the query-stripped path:

  ```python
  path = self.path.split("?", 1)[0]
  if path == "/api/transforms":
      self._send_json(200, list_transforms())
      return
  if path != "/":
      self._send_json(404, {"error": "not found"})
      return
  self._send(200, "text/html; charset=utf-8", render_page())
  ```

  No trailing-slash tolerance: `/api/transforms/` stays a 404.
- [ ] `do_POST`, `_send_json`, `_send`, `MAX_BODY_BYTES`/413 handling and
  `OPERATIONS` order are untouched.
- [ ] Do **not** re-export anything from `textkit/__init__.py` (spec §6).

## Task 3: page script posts `fn`

File: `textkit/web.py`, `render_page`.

- [ ] In the `applyOp` helper, change the request body from `op: op,` to
  `fn: op,` (the JS parameter name may stay `op`; only the JSON key changes).
- [ ] Nothing else in the page changes: ids, labels, `#title-case`, the char
  counter, Clear, `RESULT_PLACEHOLDER`, the footer count.
- [ ] Watch the f-string: literal `{`/`}` inside the script stay doubled.
- [ ] Sanity check: `python3 -c "from textkit.web import render_page; print('fn:' in render_page())"`.

## Task 4: unit tests

File: `tests/test_web.py`. Add `list_transforms` to the import block. **Do not
edit or delete the existing `op`-based tests** — they are the regression
coverage for the legacy alias (spec §1).

- [ ] New `class TestListTransforms(unittest.TestCase)`:
  - `test_payload_shape` — `list_transforms()` equals
    `{"transforms": ["initials", "reverse_words", "shout", "slugify", "title_case", "truncate"]}`
    (the one literal pin of the contract).
  - `test_only_one_key` — `list(list_transforms()) == ["transforms"]`.
  - `test_derived_from_operations` — equals `sorted(OPERATIONS)`.
  - `test_sorted` — the list equals its own `sorted()` copy.
  - `test_every_listed_name_is_callable` — `subTest` over the list:
    `handle_transform(json.dumps({"fn": name, "text": SAMPLE}).encode())`
    returns status 200 and `payload["result"] == transform(name, SAMPLE)`.
  - `test_word_count_is_not_exposed` — `"word_count"` not in the list.
- [ ] In `TestHandleTransform`, new methods (keep `_body(**payload)` as the
  helper):
  - `test_fn_field_is_accepted` — `{"fn": "slugify", "text": "Ada Lovelace"}`
    → `(200, {"result": "ada-lovelace"})`.
  - `test_op_field_still_accepted` — same with `op`, same result.
  - `test_fn_wins_over_op` — `{"fn": "shout", "op": "slugify", "text": "hi"}`
    → `{"result": "HI"}`.
  - `test_invalid_fn_is_not_rescued_by_op` — `b'{"fn": 1, "op": "shout", "text": "x"}'`
    → 400 with an `error`.
  - `test_missing_fn_is_400` — `{"text": "hi"}` → 400 with an `error`.
  - `test_unknown_fn_is_400_with_error` — `{"fn": "nope", "text": SAMPLE}` →
    400, `"nope"` in `payload["error"]`, `"result"` not in `payload`.
  - `test_non_string_fn_is_400` — `subTest` over
    `b'{"fn": 1, "text": "x"}'`, `b'{"fn": null, "text": "x"}'`,
    `b'{"fn": ["shout"], "text": "x"}'`.
  - `test_missing_text_with_fn_is_400` — `{"fn": "shout"}` → 400.
  - (malformed JSON / empty body / non-object body are already covered.)
- [ ] In `TestPlaygroundHandler`, new methods using `run_handler`:
  - `test_get_transforms_returns_json_list` — `run_handler("GET", "/api/transforms")`
    → status 200, `headers["Content-Type"] == "application/json; charset=utf-8"`,
    `json.loads(body) == list_transforms()`.
  - `test_get_transforms_with_query_string` — `/api/transforms?x=1` → 200 and
    the same body.
  - `test_get_transforms_trailing_slash_is_404` — `/api/transforms/` → 404,
    `{"error": "not found"}`.
  - `test_get_transform_singular_is_404` — `GET /api/transform` → 404.
  - `test_post_transforms_plural_is_404` — POST to `/api/transforms` → 404.
  - `test_post_transform_with_fn_ok` — POST `{"fn": "slugify", "text": "Ada Lovelace"}`
    → 200, JSON content type, `{"result": "ada-lovelace"}`.
  - `test_post_transform_unknown_fn_is_400` — POST `{"fn": "nope", "text": "x"}`
    → 400 with an `error` string.
  - `test_get_root_still_serves_the_page` is already there — leave it.
- [ ] In `TestRenderPage`, add `test_page_posts_the_fn_field`: the script
  contains `fn:` in the `JSON.stringify` block and no longer contains `op:`
  as a body key (assert on the `<script>` slice, as the sibling tests do).
- [ ] Run `python3 -m unittest discover -s tests -v` — all 75 original tests
  still pass, plus roughly 22 new ones.

## Task 5: e2e + README

- [ ] New `e2e/tests/json-api.spec.js`, header comment pointing at
  `docs/superpowers/specs/issue-19-design.md`, request-level only (no page
  interaction needed):
  - `GET /api/transforms` → 200, `content-type` header contains
    `application/json`, body equals
    `{ transforms: ["initials","reverse_words","shout","slugify","title_case","truncate"] }`.
  - every name from that response POSTs successfully: loop, expect 200 and a
    string `result`.
  - `POST /api/transform` `{fn: "title_case", text: "a tale of two cities"}`
    → 200 `{ result: "A Tale of Two Cities" }`.
  - `POST /api/transform` `{fn: "nope", text: "x"}` → 400, `typeof body.error === "string"`.
  - `POST /api/transform` malformed body `"{not json"` → 400 with a string
    `error`.
  - `GET /api/transforms/` → 404.
- [ ] `e2e/tests/playground.spec.js` and `e2e/tests/title-case.spec.js` keep
  posting `op` — leave them alone; they are the alias's e2e coverage.
- [ ] `README.md`: add a short `## HTTP API` section documenting both
  endpoints, the request/response shapes, the 400 shape, and one sentence
  noting `op` is a deprecated alias of `fn`. Two `curl` examples, no more.

## Task 6: changelog, verification, commit

- [ ] Follow the `changelog` skill — append to the **end** of `CHANGELOG.md`,
  one line per new public function, using the current UTC date:

  ```
  - 2026-08-03: list_transforms — GET /api/transforms отдаёт отсортированный список преобразований
  - 2026-08-03: handle_transform (fn) — POST /api/transform принимает поле fn (op — устаревший синоним)
  ```

- [ ] `python3 -m unittest discover -s tests -v` — green.
- [ ] Manual check against a running server
  (`TEXTKIT_PORT=3000 python3 -m textkit.web`, bind stays `0.0.0.0`):
  - `curl -s -i 127.0.0.1:3000/api/transforms` → 200, JSON content type, the
    six sorted names.
  - `curl -s -X POST 127.0.0.1:3000/api/transform -d '{"fn":"slugify","text":"Ada Lovelace"}'`
    → `{"result": "ada-lovelace"}`.
  - `curl -s -o /dev/null -w '%{http_code}\n' -X POST 127.0.0.1:3000/api/transform -d '{"fn":"nope","text":"x"}'`
    → `400`.
  - `curl -s 127.0.0.1:3000/ | grep -c 'fn:'` → `1`.
- [ ] Playwright from `e2e/` against that server:
  `E2E_BASE_URL=http://localhost:3000 npx playwright test`. First run needs
  `npm ci` and
  `PLAYWRIGHT_BROWSERS_PATH=/home/sandbox/.cache/ms-playwright npx playwright install chromium`
  (the default `/opt/pw-browsers` is read-only and `--with-deps` needs root).
- [ ] Confirm no `__pycache__/` or `*.pyc` is staged; single commit; **do not
  push**.

## Files touched

| file | change |
| --- | --- |
| `textkit/web.py` | `fn`/`op` lookup in `handle_transform`, new `list_transforms`, `do_GET` routing, page script posts `fn` |
| `tests/test_web.py` | `TestListTransforms`, `fn` cases in `TestHandleTransform`, routing cases in `TestPlaygroundHandler`, one `TestRenderPage` assertion |
| `e2e/tests/json-api.spec.js` | new request-level spec |
| `README.md` | `## HTTP API` section |
| `CHANGELOG.md` | two entries |

Not touched: `textkit/core.py`, `textkit/__init__.py`, `tests/test_core.py`,
the other e2e specs, `OPERATIONS` order, the footer count.

## Risks / watch-outs

- **The contract is consumed by another repo.** `{"transforms": [...]}`,
  `{"result": ...}` and `{"error": ...}` are exact; do not add a `count`, an
  `ok` flag, or nest anything.
- The list includes `truncate` — a deliberate reading of "single-argument text
  transforms" argued in spec §3. If review disagrees, it is a one-line change
  plus two assertions; raise it before the frontend ships against six names.
- `render_page` is one big f-string: an unbalanced literal brace in the script
  breaks page rendering at call time, not at import.
- `do_GET` is the only place that decides the HTML vs JSON content type —
  after the refactor, re-check that `/` still returns
  `text/html; charset=utf-8` (`test_get_root_serves_page` covers it).
- Reordering `OPERATIONS` would break `e2e/tests/playground.spec.js`, which
  pins the `<select>` order; `sorted()` in `list_transforms` is what makes the
  API order independent of it.
- `payload.get("fn") or payload.get("op")` is the tempting one-liner and is
  wrong: `""` and `0` fall through to `op`. Use the `in` check.
