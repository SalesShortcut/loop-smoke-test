# snake_case transform — design

Issue: #21 (`.loop/task.md`)
Date: 2026-08-04
Status: approved

## What we are building

A new pure text operation in the textkit library and its exposure through the
existing web playground:

- `textkit.core.snake_case(text)` → the text folded to ASCII, lowercased, with
  every run of non-alphanumeric characters replaced by a single `_` and no
  leading or trailing `_`. `snake_case("Café au lait") == "cafe_au_lait"`.
- The ASCII-folding + collapsing logic is factored out of `slugify` into one
  private helper that both functions call, so the two can never drift apart in
  how they treat accents, punctuation or non-Latin scripts. `slugify`'s
  observable behaviour does not change.
- `snake_case` is exported from `textkit/__init__.py` and registered in
  `web.OPERATIONS`, which is the single registry behind both the playground's
  operation picker and the JSON API (`GET /api/transforms`,
  `POST /api/transform`).
- Unit tests in `tests/test_core.py` and `tests/test_web.py`, a new Playwright
  spec, and the four existing e2e/unit assertions that hard-code the operation
  set updated from six names to seven.

## Why

`slugify` already produces a hyphenated ASCII slug, which is the right shape
for URLs and the wrong shape for identifiers: a user who wants
`cafe_au_lait` has to hand-edit the hyphens. `snake_case` is the same
normalisation with `_` as the separator, so the cheapest correct
implementation is to share the normalisation rather than to re-derive it —
which is also what keeps `slugify("Café")` and `snake_case("Café")` from
answering the accent question differently a year from now.

The web side is one line because `OPERATIONS` drives every surface: the
`<option>` list rendered into the page, the footer count, `GET /api/transforms`
and the names accepted by `POST /api/transform`.

## Starting point (what already exists)

`textkit/core.py`:

- `slugify(text)` — the only function that folds to ASCII:

  ```python
  ascii_text = (
      unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
  )
  return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
  ```

  Pinned by `tests/test_core.py::TestSlugify`: `"Ada Lovelace"` →
  `ada-lovelace`, `"  Hello, World!!  "` → `hello-world`, `""` → `""`,
  `"Café au lait"` → `cafe-au-lait`, `"Привет"` → `""`, `"Привет ada"` → `ada`.
- Also present: `word_count`, `shout`, `title_case`, `initials`,
  `reverse_words`, `truncate`. `re` and `unicodedata` are already imported.

`textkit/__init__.py` re-exports the seven core functions (imports +
`__all__`, both alphabetical).

`textkit/web.py`:

- `OPERATIONS` — six entries in insertion order: `slugify`, `shout`,
  `initials`, `reverse_words`, `truncate` (a lambda binding
  `TRUNCATE_WIDTH = 20`), `title_case`. Insertion order drives the `<select>`
  option order, which e2e pins.
- `transform(op, text)` dispatches through it; unknown name → `ValueError`.
- `handle_transform(body)` reads `fn` (canonical) or `op` (legacy alias) and
  returns `(200, {"result": ...})` / `(400, {"error": ...})`.
- `list_transforms()` returns `{"transforms": sorted(OPERATIONS)}`.
- `render_page()` renders one `<option value="{op}">{op}</option>` per entry
  into `<select id="op">`, an `<button id="apply">` / `<button id="clear">` /
  `<button id="title-case">` row, `<output id="result">` and
  `<footer id="footer">textkit playground · {len(OPERATIONS)} operations</footer>`.
  The page script POSTs `{fn, text}` to `/api/transform`.
- Routing: `GET /` → page, `GET /api/transforms` → JSON list,
  `POST /api/transform` → transform. **Everything else, including `POST /`, is
  `404 {"error": "not found"}`.**

Baseline: `python3 -m unittest discover -s tests -v` → **97 tests, green**.

## Locked decisions

### 1. One private helper, parameterised by separator

New module-private function in `textkit/core.py`, placed immediately above
`slugify`:

```python
def _ascii_slug(text: str, separator: str) -> str:
    ascii_text = (
        unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    )
    return re.sub(r"[^a-z0-9]+", separator, ascii_text.lower()).strip(separator)
```

`slugify` becomes `return _ascii_slug(text, "-")` and `snake_case` becomes
`return _ascii_slug(text, "_")`. Both keep their own docstrings with an
`Example:` section (CLAUDE.md); the helper is private, needs no `Example:`
section, and is **not** exported from `textkit/__init__.py`.

This satisfies requirement 4 literally: the folding and collapsing live in one
place. The body above is byte-for-byte the current `slugify` body with `"-"`
replaced by the parameter, so `slugify`'s six pinned behaviours are unchanged
by construction.

Rejected: `snake_case = lambda t: slugify(t).replace("-", "_")` — correct
today, but it makes `snake_case` a derivative of a *published* output rather
than of the shared normalisation, and it breaks silently the day `slugify`'s
separator changes. Rejected: a public `separator=` parameter on `slugify` —
changes an existing public signature (explicitly rejected in the issue).

The helper is only ever called with `"-"` or `"_"`. Both are literal in a
`re.sub` replacement string and safe for `str.strip`; the helper does not
validate this because it is private.

### 2. `snake_case` semantics — exactly `slugify`'s, with `_`

For every input, `snake_case(text) == slugify(text).replace("-", "_")`. That
identity is asserted as a test, not just stated, because it is the concrete
form of "shared, not duplicated".

Consequences, all intended:

| input | result |
| --- | --- |
| `"Ada Lovelace"` | `"ada_lovelace"` |
| `"Café au lait"` | `"cafe_au_lait"` |
| `""` | `""` |
| `"  Hello, World!!  "` | `"hello_world"` |
| `"ada-lovelace"` | `"ada_lovelace"` (hyphens are separators too) |
| `"snake_case already"` | `"snake_case_already"` (a literal `_` is a separator run, so runs collapse) |
| `"Version 2 Beta"` | `"version_2_beta"` (digits are kept) |
| `"Привет"` | `""` |
| `"Привет ada"` | `"ada"` |

No identifier-safety extras: a result starting with a digit (`snake_case("2 cats")`
→ `"2_cats"`) is returned as is, and no Python keyword check is performed. The
issue asks for a snake_case *string*, and adding a leading-underscore rule
would break the `slugify` identity above. Nothing else in the repo consumes
the value.

### 3. The playground surface is a new `<option>`, not a new `<button>`

The issue's requirement 5 and its Notes state that registering
`"snake_case": core.snake_case` in `OPERATIONS` is what "makes the button
appear on the page", and the Approach section lists that registration as the
*entire* web change. In the code as it stands, `OPERATIONS` renders as
`<option>` elements inside `<select id="op">`, driven by `#apply` — there are
no per-operation buttons. `#title-case` is the single exception, added by
issue #15 for its own reasons.

Decision: register in `OPERATIONS` and change nothing else in `render_page`.
The user picks `snake_case` in `#op` and presses **Apply**. The issue's phrase
"a `snake_case` button alongside the existing operations" is read as "the
operation appears in the picker alongside the existing operations", which is
the only reading consistent with its own Approach ("one registration covers
both surfaces") and with "Changing the look of the playground beyond the one
new button" being out of scope.

Rejected: adding a dedicated `<button id="snake-case">` mirroring
`#title-case`. It is UI the Approach section does not describe, it would
duplicate an entry the picker already offers, and it invents a label and a
document position the issue never fixes. If review wants it anyway, it is a
follow-up of the same size as issue #15's button — flag it before shipping
rather than after.

### 4. Position in `OPERATIONS`: appended last

The entry goes after `title_case`, at the end of the dict. Option order in the
`<select>` therefore becomes:

```
slugify, shout, initials, reverse_words, truncate, title_case, snake_case
```

Precedent: issue #15 appended `title_case` at the end for exactly this reason
— `e2e/tests/playground.spec.js` asserts the option list equals the keys of
its own `OPERATIONS` map *in order*, so appending is the smallest safe diff.
Existing entries are never reordered.

`GET /api/transforms` is unaffected by the position: it sorts, giving

```json
{"transforms": ["initials", "reverse_words", "shout", "slugify", "snake_case", "title_case", "truncate"]}
```

(`slugify` sorts before `snake_case`: `l` < `n`.)

### 5. The JSON path is `POST /api/transform`, with both field names

The issue's acceptance criterion says `POST /` with `{"op": "snake_case",
"text": "Ada Lovelace"}`. `POST /` is a `404 {"error": "not found"}` in this
codebase and stays one; the transform endpoint is `POST /api/transform`
(spec issue-19 §4). `op` is still accepted there as the legacy alias of `fn`,
so the issue's body works verbatim at the real path. Both field names are
verified for `snake_case`:

- `POST /api/transform` `{"fn": "snake_case", "text": "Ada Lovelace"}` → `200 {"result": "ada_lovelace"}`
- `POST /api/transform` `{"op": "snake_case", "text": "Ada Lovelace"}` → `200 {"result": "ada_lovelace"}`

No new route, no change to `handle_transform`, `transform`, `list_transforms`
or the error wording.

### 6. Four existing assertions move from six operations to seven

Adding an entry to `OPERATIONS` is a visible change to three derived values.
All four places that hard-code them must move together, or the suite goes red:

| file | assertion | 6 → 7 |
| --- | --- | --- |
| `tests/test_web.py` | `TestTransform.test_supported_ops` | name list gains `snake_case` |
| `tests/test_web.py` | `TestListTransforms.test_payload_shape` | sorted list gains `snake_case` |
| `tests/test_web.py` | `TestRenderPage.test_footer_counts_the_operations` | `· 6 operations` → `· 7 operations` |
| `e2e/tests/footer.spec.js` | `FOOTER_TEXT` | `· 6 operations` → `· 7 operations` |
| `e2e/tests/json-api.spec.js` | `NAMES` | sorted list gains `snake_case` |
| `e2e/tests/issue-19-consumer.spec.js` | `expect(transforms).toEqual([...])` | sorted list gains `snake_case` |
| `e2e/tests/playground.spec.js` | `OPERATIONS` map | gains `snake_case: "ada_lovelace_was_a_mathematician"` as the **last** key |

The footer text itself is not otherwise changed; `e2e/tests/footer.spec.js`'s
"count matches the number of options" test is derived and needs no edit, and
so do `test_every_op_returns_200`, `test_one_option_per_operation` and
`test_every_listed_name_is_callable`, which iterate `OPERATIONS`.

### 7. House rules

- Standard library only; no new imports anywhere (`re` and `unicodedata` are
  already in `core.py`).
- `snake_case`'s docstring carries an `Example:` section (CLAUDE.md).
- `snake_case` is added to both the `from .core import (...)` list and
  `__all__` in `textkit/__init__.py`, alphabetically between `slugify` and
  `title_case`. `_ascii_slug` is not.
- One `CHANGELOG.md` line appended at the end per the `changelog` skill, in
  the feature commit: `- 2026-08-04: snake_case — идентификатор в snake_case из произвольной строки`
  (use the actual current UTC date if it has moved on). No entry for the
  private helper.
- Single commit, message prefixed `[textkit] `. No `__pycache__/`, no `*.pyc`.
  No push.

## Acceptance criteria

1. `core.snake_case("Café au lait") == "cafe_au_lait"` and
   `core.snake_case("") == ""`.
2. `core.snake_case(text) == core.slugify(text).replace("-", "_")` for at
   least: `""`, `"Ada Lovelace"`, `"  Hello, World!!  "`, `"Café au lait"`,
   `"Привет"`, `"Привет ada"`, `"ada-lovelace"`, `"snake_case already"`,
   `"Version 2 Beta"`.
3. The result never starts or ends with `_`, never contains `__`, and consists
   only of `[a-z0-9_]`.
4. `slugify` is unchanged: `TestSlugify` passes untouched, and both `slugify`
   and `snake_case` call the same private helper (no duplicated
   `unicodedata.normalize`/`re.sub` pair anywhere in `core.py`).
5. `from textkit import snake_case` works, and `snake_case` is in
   `textkit.__all__`. `_ascii_slug` is not exported.
6. `sorted(web.OPERATIONS) == ["initials", "reverse_words", "shout",
   "slugify", "snake_case", "title_case", "truncate"]`, and
   `web.OPERATIONS["snake_case"] is core.snake_case` (registered directly, not
   wrapped in a lambda — it takes only the text).
7. `GET /api/transforms` returns those seven names, sorted.
8. `POST /api/transform` with `{"fn": "snake_case", "text": "Ada Lovelace"}`
   and with `{"op": "snake_case", "text": "Ada Lovelace"}` both return
   `200 {"result": "ada_lovelace"}` with
   `Content-Type: application/json; charset=utf-8`.
9. `render_page()` contains `<option value="snake_case">snake_case</option>`
   as the last option, and the footer reads
   `textkit playground · 7 operations`.
10. Every existing operation still returns what it returned before, under the
    same JSON name: `slugify` → `ada-lovelace` (still hyphens),
    `title_case`, `shout`, `initials`, `reverse_words`, `truncate` unchanged;
    `#apply`, `#clear`, `#title-case`, the char counter and
    `RESULT_PLACEHOLDER` untouched.
11. `python3 -m unittest discover -s tests -v` is green: the 97 baseline tests
    still pass with only the three assertion updates from §6, plus the new
    ones.
12. The Playwright suite is green, including a new spec that drives the
    playground: type `Café au lait`, choose `snake_case`, press Apply, read
    `cafe_au_lait` from `#result`.
13. `CHANGELOG.md` gains its line in the feature commit, in the skill's
    format.

## Main user scenario

1. A user opens `http://localhost:3000/`.
2. They type `Café au lait` into `#text`.
3. They choose `snake_case` in the `#op` picker — it is listed there beside
   `slugify`, `shout`, `initials`, `reverse_words`, `truncate` and
   `title_case`.
4. They press **Apply**. The page POSTs
   `{"fn": "snake_case", "text": "Café au lait"}` to `/api/transform`.
5. `#result` shows `cafe_au_lait`.
6. They switch the picker back to `slugify` and press Apply again:
   `#result` shows `cafe-au-lait`, exactly as before this change.

## Out of scope

- Any other new text operation.
- A dedicated `<button>` for `snake_case` (see §3), any restyling, reordering
  or relabelling of the playground, and any change to `#apply`, `#clear`,
  `#title-case`, the char counter, the placeholder or the footer *format*.
- A CLI entry point for `snake_case`.
- Identifier hardening: leading-digit prefixes, Python-keyword avoidance,
  length limits, `camelCase` → `snake_case` word splitting
  (`snake_case("myVariableName")` returns `"myvariablename"`, by design — the
  transform is separator-based, not case-boundary-based).
- Changing `slugify`'s public signature, adding a `separator` parameter, or
  exporting `_ascii_slug`.
- New routes (`POST /` stays a 404), new request fields, changes to the
  `fn`/`op` aliasing or to any error wording.
- `word_count` stays unexposed in `OPERATIONS`.
- README changes: the `## HTTP API` table documents shapes, not the operation
  list, so it stays accurate as written.
