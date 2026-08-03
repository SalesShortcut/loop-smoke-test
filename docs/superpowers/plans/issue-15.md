# title-case transform — implementation plan

Spec: `docs/superpowers/specs/issue-15-design.md`
(source of truth; its Locked decisions are binding).
Issue: #15

Do the tasks in order; each one leaves the suite green. Everything lands in a
single commit at Task 5, message prefixed `[textkit] ` per `CLAUDE.md`.

## Task 1: `title_case` in the library

- [ ] In `textkit/core.py` add a module-level constant near the top:
  `TITLE_CASE_CONNECTORS = frozenset({"a", "an", "the", "and", "or", "of", "in", "on"})`.
- [ ] Add `title_case(text: str) -> str` (place it after `shout`, keeping the
  file's rough "simple transforms first" order). Shape:

  ```python
  def title_case(text: str) -> str:
      """Return text with every word capitalised, keeping connectors lowercase.

      Example:
          >>> title_case("ada lovelace and the analytical engine")
          'Ada Lovelace and the Analytical Engine'
      """
      words = text.split()
      return " ".join(
          word.lower() if index and word.lower() in TITLE_CASE_CONNECTORS
          else word[0].upper() + word[1:].lower()
          for index, word in enumerate(words)
      )
  ```

  (Write the docstring in English — the snippet above is a shape sketch, not
  copy-paste text. The `Example:` section is mandatory per `CLAUDE.md`.)
- [ ] Export it: add `title_case` to both the `from .core import (...)` list
  and `__all__` in `textkit/__init__.py`, alphabetically between `slugify`
  and `truncate`.
- [ ] Standard library only; no new imports needed.

## Task 2: unit tests for `title_case`

- [ ] In `tests/test_core.py` add `title_case` to the `from textkit import (...)`
  block and a `class TestTitleCase(unittest.TestCase)` placed to match the
  file's ordering. Cover, one test method each:
  - `test_empty` — `title_case("") == ""`
  - `test_single_word` — `title_case("ada") == "Ada"`
  - `test_connector_word_first` — `title_case("the analytical engine") == "The Analytical Engine"`
  - `test_connectors_stay_lowercase` — `title_case("ada lovelace and the analytical engine") == "Ada Lovelace and the Analytical Engine"`
  - `test_all_caps_input_is_normalised` — `title_case("ADA LOVELACE") == "Ada Lovelace"`
  - `test_every_connector_is_lowercased` — loop over
    `TITLE_CASE_CONNECTORS` with `subTest`, asserting
    `title_case(f"start {word} end") == f"Start {word} End"`
  - `test_extra_whitespace_collapses` — `title_case("  grace   brewster  hopper ") == "Grace Brewster Hopper"`
  - `test_scenario_from_spec` — `title_case("a tale of two cities") == "A Tale of Two Cities"`
- [ ] Run `python3 -m unittest discover -s tests -v` — green.

## Task 3: playground wiring

- [ ] In `textkit/web.py` append `"title_case": core.title_case,` to
  `OPERATIONS` **after** the `truncate` entry (order drives the `<select>`).
- [ ] In `render_page`, add
  `<button id="title-case" type="button">Title Case</button>` immediately
  after the `#clear` button, inside the same `<p>`.
- [ ] Refactor the page script: pull the body of the `#apply` click handler
  into `const applyOp = async (op) => {...}` that reads `#text`, POSTs
  `{op, text}` to `/api/transform` and writes `data.result` / `data.error`
  into `#result` (keep the existing `try/catch` → `String(err)` fallback).
  Then wire:
  - `#apply` → `applyOp(document.getElementById("op").value)`
  - `#title-case` → `applyOp("title_case")`
  Do not touch the `#op` value from the new handler (locked decision).
  Mind the f-string: literal braces in the script must stay doubled.
- [ ] No changes to `handle_transform`, routing, `RESULT_PLACEHOLDER`, the
  char counter or Clear.

## Task 4: update and extend the web tests

Files: `tests/test_web.py`, `e2e/tests/*`.

- [ ] `tests/test_web.py`, existing tests that must be updated:
  - `test_supported_ops` → expected list becomes
    `["initials", "reverse_words", "shout", "slugify", "title_case", "truncate"]`.
  - `test_footer_counts_the_operations` → `6 operations`.
- [ ] `tests/test_web.py`, new assertions:
  - `test_title_case_matches_core` in `TestTransform`:
    `transform("title_case", SAMPLE) == core.title_case(SAMPLE)`
    (`SAMPLE` title-cases to `"Ada Lovelace Was a Mathematician"` — pin that
    literal in one extra assertion).
  - In `TestRenderPage.test_required_elements` add the fragment
    `'<button id="title-case"'`.
  - `test_title_case_button_is_labelled_and_wired`, mirroring
    `test_clear_button_is_labelled_and_wired`: the page contains
    `<button id="title-case" type="button">Title Case</button>`, the script
    references `getElementById("title-case")` and the string `"title_case"`,
    and the button follows `#clear` in document order
    (`page.index('id="clear"') < page.index('id="title-case"')`).
  - `test_every_op_returns_200` and `test_one_option_per_operation` iterate
    `OPERATIONS`, so they cover the new op with no edit.
- [ ] `e2e/tests/footer.spec.js`: `FOOTER_TEXT` → `"textkit playground · 6 operations"`.
- [ ] `e2e/tests/playground.spec.js`: add `title_case: "Ada Lovelace Was a Mathematician"`
  as the **last** entry of the `OPERATIONS` map (the page-elements test
  asserts the option list equals `Object.keys(OPERATIONS)` in order, and the
  critical-path loop then covers the op via the select).
- [ ] New `e2e/tests/title-case.spec.js`, header comment pointing at
  `docs/superpowers/specs/issue-15-design.md`, importing `PLACEHOLDER` from
  `./constants`:
  - main scenario — goto `/`, `fill("#text", "ada lovelace and the analytical engine")`,
    `waitForResponse("**/api/transform")` around `click("#title-case")`,
    expect `#result` to have text `Ada Lovelace and the Analytical Engine`.
  - `button#title-case` is visible and sits after `button#clear`
    (`compareDocumentPosition`, as in `footer.spec.js`).
  - the button works without touching `#op`: after the click,
    `#op` still has its default value (`slugify`).
  - connector first word — `"the analytical engine"` → `"The Analytical Engine"`.
  - Clear still works after a title-case run: `#text` empty, `#result` back to
    `PLACEHOLDER`.
  - request-level: `POST /api/transform` with
    `{op: "title_case", text: "a tale of two cities"}` → 200 and
    `{result: "A Tale of Two Cities"}`.

## Task 5: changelog, verification, commit

- [ ] Follow the `changelog` skill: append **one** line to the end of
  `CHANGELOG.md`:
  `- 2026-08-03: title_case — заглавные буквы в словах, служебные слова строчными` .
  (Use the actual current UTC date if it has moved on.)
- [ ] `python3 -m unittest discover -s tests -v` — expect all green
  (65 existing + the new ones).
- [ ] Manual/e2e check: `TEXTKIT_PORT=3000 python3 -m textkit.web`, then
  `curl -s -X POST 127.0.0.1:3000/api/transform -d '{"op":"title_case","text":"a tale of two cities"}'`
  → `{"result": "A Tale of Two Cities"}`, and `curl -s 127.0.0.1:3000/ | grep title-case`.
- [ ] Playwright suite from `e2e/` against a running server on port 3000
  (`E2E_BASE_URL=http://localhost:3000 npx playwright test`) — green.
- [ ] Confirm no `__pycache__/` or `*.pyc` is staged, then commit everything
  in one commit:
  `[textkit] feat: title_case transform and playground button`.
  Do not push.

## Files touched

| file | change |
| --- | --- |
| `textkit/core.py` | `TITLE_CASE_CONNECTORS`, `title_case` |
| `textkit/__init__.py` | import + `__all__` |
| `textkit/web.py` | `OPERATIONS` entry, `#title-case` button, `applyOp` refactor |
| `tests/test_core.py` | `TestTitleCase` |
| `tests/test_web.py` | op list, footer count, transform + markup assertions |
| `e2e/tests/playground.spec.js` | new expected op |
| `e2e/tests/footer.spec.js` | 5 → 6 operations |
| `e2e/tests/title-case.spec.js` | new spec |
| `CHANGELOG.md` | one entry |

## Risks / watch-outs

- `render_page` is one big f-string: every literal `{`/`}` in the added
  JavaScript must be doubled, or the page fails to render at import-time use.
- Two footer assertions (unit + e2e) and two op-list assertions (unit +
  e2e) hard-code the operation count/order — missing one of the four is the
  most likely cause of a red suite.
- `word[0]` is safe only because `str.split()` never yields empty strings;
  do not switch to `split(" ")`.
