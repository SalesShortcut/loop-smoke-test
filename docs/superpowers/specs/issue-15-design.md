# title-case transform — design

Issue: #15 (`.loop/task.md`)
Date: 2026-08-03
Status: approved

## What we are building

A `title_case` transform in the `textkit` library — "ada lovelace and the
analytical engine" → "Ada Lovelace and the Analytical Engine" — plus a
dedicated button in the web playground that applies it to the textarea
content, and unit + e2e coverage for both.

## Why

`textkit` already offers `shout` (all upper) and `slugify` (all lower); there
is no way to normalise a string into headline form. Title casing is the
missing everyday transform, and the playground is where the library's
operations are demonstrated, so it has to be reachable from the page.

## Locked decisions

### Library

- New public function in `textkit/core.py`:
  `title_case(text: str) -> str`, exported from `textkit/__init__.py` and
  listed in `__all__` (alphabetical position: after `slugify`, before
  `truncate`).
- Casing rule: each word becomes `word[0].upper() + word[1:].lower()`.
- Connector words stay lowercase **unless they are the first word**. The
  connector set is exactly the nine words named in the issue, matched
  case-insensitively:
  `a, an, the, and, or, of, in, on`.
  It lives in `core.py` as a module-level frozenset constant
  (`TITLE_CASE_CONNECTORS`) so tests and future edits have one source of truth.
- Position is the *only* thing that changes the rule. There is no sentence
  detection (a connector after a full stop stays lowercase) and no
  "capitalise the last word" rule.
- Words are whitespace-separated: the implementation is
  `" ".join(...)` over `text.split()`, matching the existing house style of
  `initials` and `reverse_words`. Consequence, accepted deliberately: runs of
  whitespace collapse to a single space and leading/trailing whitespace is
  stripped. Newlines are therefore not preserved.
- Punctuation and non-letters are not special-cased: they are simply carried
  along by the slice (`"o'neill"` → `"O'neill"`, `"3rd"` → `"3rd"`,
  `"co-op"` → `"Co-op"` — hyphenated parts are *not* separately capitalised).
- The docstring carries an `Example:` section with a doctest-style call and
  result, per `CLAUDE.md`.

Worked examples (these are the acceptance examples):

| input | output |
| --- | --- |
| `""` | `""` |
| `"ada"` | `"Ada"` |
| `"the analytical engine"` | `"The Analytical Engine"` |
| `"ada lovelace and the analytical engine"` | `"Ada Lovelace and the Analytical Engine"` |
| `"ADA LOVELACE"` | `"Ada Lovelace"` |
| `"a tale of two cities"` | `"A Tale of Two Cities"` |
| `"  grace   brewster  hopper "` | `"Grace Brewster Hopper"` |
| `"Ada Lovelace was a mathematician"` | `"Ada Lovelace Was a Mathematician"` |

### Playground

- `title_case` is added to the `OPERATIONS` mapping in `textkit/web.py`,
  **appended after `truncate`** (dict order drives the `<select>` option
  order, which e2e pins). It therefore also becomes selectable in `#op` and
  callable as `{"op": "title_case"}` on `POST /api/transform`, like every
  other operation.
- A new button `<button id="title-case" type="button">Title Case</button>`
  sits in the same `<p>` as `#apply` and `#clear`, after `#clear`. The id
  `title-case` is the stable e2e handle the issue asks for.
- Clicking it POSTs `{"op": "title_case", "text": <textarea value>}` to
  `/api/transform` and writes the response into `#result` — exactly the code
  path `#apply` uses. To avoid duplicating that path, the existing inline
  click handler is factored into one `applyOp(op)` helper in the page script;
  `#apply` calls `applyOp(document.getElementById("op").value)` and
  `#title-case` calls `applyOp("title_case")`.
- The button does **not** change the `#op` select value. Rationale: the select
  is input for `#apply` only, and mutating it from another control is a side
  effect nobody asked for. Consequence: after clicking Title Case the select
  may still read `slugify` while the result is title-cased. Accepted.
- Error handling, the `413`/`400` paths, `RESULT_PLACEHOLDER`, the char
  counter and the Clear behaviour are untouched.
- The footer text is generated from `len(OPERATIONS)`, so it becomes
  `textkit playground · 6 operations` automatically. Both the unit test and
  the e2e constant that pin `5` must be updated to `6`.

### Interpretation note

The issue says the new button should follow "the pattern of the existing
transform buttons". The playground has no per-transform buttons today — it has
one `<select id="op">` plus a single `#apply` button. This design satisfies
both readings: the transform joins the select like every other operation
(existing pattern) *and* gets its own id-addressable button (literal request).

## Acceptance criteria

1. `from textkit import title_case` works; `title_case` is in
   `textkit.__all__`.
2. Every row of the worked-examples table above holds.
3. `title_case("")` returns `""` (no exception).
4. A connector word in first position is capitalised
   (`title_case("the end")== "The End"`); the same word elsewhere is not
   (`title_case("end of the road") == "End of the Road"`).
5. `transform("title_case", text)` equals `core.title_case(text)`, and
   `sorted(OPERATIONS)` is
   `["initials", "reverse_words", "shout", "slugify", "title_case", "truncate"]`.
6. `POST /api/transform` with `{"op": "title_case", "text": "a tale of two cities"}`
   returns `200 {"result": "A Tale of Two Cities"}`.
7. The rendered page contains `<button id="title-case" type="button">Title Case</button>`
   after the `#clear` button, and an `<option value="title_case">`.
8. In the browser: typing `ada lovelace and the analytical engine` and
   clicking `#title-case` puts `Ada Lovelace and the Analytical Engine` in
   `#result`, without the user touching `#op`.
9. The footer reads `textkit playground · 6 operations`.
10. `python3 -m unittest discover -s tests -v` is green (65 existing tests
    still pass, adjusted where they pin the operation count), and the
    Playwright suite is green.
11. `CHANGELOG.md` gains one entry in the skill's format, in the feature
    commit.

## Main user scenario

1. Open `/`.
2. Type `ada lovelace and the analytical engine` into `#text`.
3. Click **Title Case**.
4. `#result` shows `Ada Lovelace and the Analytical Engine`.
5. Click **Clear** — input empties and `#result` returns to the placeholder,
   as before.

## Out of scope

- Locale-aware or Unicode-aware title casing beyond Python's `str.upper()` /
  `str.lower()`.
- A configurable or user-editable connector list; per-language connector sets.
- Capitalising parts of hyphenated or slash-separated compounds.
- Preserving the original whitespace/newline layout of the input.
- Styling of the new button; layout or CSS work of any kind.
- Buttons for the other five operations.
