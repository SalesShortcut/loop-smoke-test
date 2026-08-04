# snake_case transform — design

Issue: #21 (`.loop/task.md`)
Date: 2026-08-04
Status: approved

## Goal

`textkit` gains a public `snake_case(text)` function that turns any phrase into a
snake_case identifier (`"Café au lait"` → `"cafe_au_lait"`), and the web playground
exposes it as one more operation — selectable on the page and callable as
`{"fn": "snake_case"}` (or the legacy `{"op": "snake_case"}`) on
`POST /api/transform`.

## Why

`textkit/core.py` today offers `word_count`, `slugify`, `shout`, `title_case`,
`initials`, `reverse_words` and `truncate`. The only normalising transform is
`slugify`, which emits hyphens — fine for URLs, wrong for identifiers. Producing
`ada_lovelace` from `Ada Lovelace` currently requires the caller to post-process
`slugify`'s output. This adds the missing operation, and does it by sharing
`slugify`'s normalisation so the two can never disagree about accents or
punctuation.

## Context

Everything below was read out of the repository, not assumed.

- `textkit/core.py` — pure functions, standard library only (`re`, `unicodedata`).
  `slugify` is currently:

  ```python
  ascii_text = (
      unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
  )
  return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
  ```

- `textkit/__init__.py` re-exports the public functions in one alphabetical
  `from .core import (...)` block and repeats them in `__all__`.
- `textkit/web.py` holds `OPERATIONS`, a `dict[str, Callable[[str], str]]`. It is
  the single registry behind three surfaces:
  1. `transform(op, text)` → the `POST /api/transform` handler,
  2. `list_transforms()` → `GET /api/transforms` (`sorted(OPERATIONS)`),
  3. `render_page()` → one `<option value="…">` per key, **in dict insertion
     order**, plus the footer text `textkit playground · {len(OPERATIONS)} operations`.
- `tests/` uses `unittest` only (no pytest, no doctest runner). Command from
  `.loop.yml`: `python3 -m unittest discover -s tests -v`. Baseline on this branch:
  **97 tests, OK**.
- `e2e/` is a Playwright suite driven by `E2E_BASE_URL` (default
  `http://localhost:3000`). `e2e/node_modules` is **not** present in this sandbox —
  it needs `npm ci` plus a browser install before it can run.
- `CLAUDE.md` (binding): standard library only; every new **public** function's
  docstring must carry an `Example:` section; new public functions are exported from
  `textkit/__init__.py`; every commit message starts with `[textkit] `; never commit
  `__pycache__/` or `*.pyc`. Feature work also follows the `changelog` skill
  (`.claude/skills/changelog/SKILL.md`): one line appended to the **end** of
  `CHANGELOG.md`, format `- YYYY-MM-DD: <имя функции> — <описание на русском>`, in
  the feature commit.

### Two places where the issue text does not match the code

The issue was written against a slightly stale mental model of the playground. Both
mismatches are resolved here so the implementer does not have to guess.

1. **"buttons" vs the select.** The issue says `OPERATIONS` "drives the operation
   buttons on the page" and asks for "a `snake_case` button". `render_page()` renders
   `OPERATIONS` as `<option>` elements inside `<select id="op">`; the only per-operation
   button is `#title-case`, added by issue #15 because that issue explicitly asked for
   an id-addressable button. Registering a key in `OPERATIONS` cannot create a button.

   **Locked decision: `snake_case` gets an `<option value="snake_case">` in `#op` and
   nothing else — no new button.** This follows the issue's own Approach ("one
   registration covers both surfaces") and its Notes ("the button and the API endpoint
   are one change, not two"); adding a dedicated button would be a second, separate
   change with a newly invented selector, which the Notes explicitly warn against
   ("follow them rather than inventing new ones"). The user reaches the new operation
   the same way they reach `slugify`: pick it in `#op`, press **Apply**.

2. **`POST /`** is a 404. The transform endpoint is `POST /api/transform`; the
   canonical field is `fn`, and `op` is kept as a legacy alias (`fn` wins when both are
   present). The issue's `POST /` with `{"op": "snake_case", "text": "Ada Lovelace"}`
   is read as `POST /api/transform` with that body — which works, via the alias. The
   acceptance criteria below pin both `fn` and `op`.

## Approach

Extract the normalisation `slugify` already performs into a private, separator-parameterised
helper in `core.py`, and build both public functions on it:

```python
def _ascii_slug(text: str, separator: str) -> str:
    ascii_text = (
        unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    )
    return re.sub(r"[^a-z0-9]+", separator, ascii_text.lower()).strip(separator)
```

`slugify` becomes `return _ascii_slug(text, "-")`; `snake_case` becomes
`return _ascii_slug(text, "_")`. `slugify`'s observable behaviour is byte-for-byte
unchanged — verified by running the extracted helper against every input in the
existing `TestSlugify` suite plus `"__a__"`, `"a_b"`, `"Ada_Lovelace"`, `"1.5 kg"` and
`"---"`; all matched.

Then register the operation in `web.py`:

```python
OPERATIONS = {
    ...,
    "title_case": core.title_case,
    "snake_case": core.snake_case,
}
```

**Appended last**, after `title_case`. Dict order is the `<option>` order, which
`e2e/tests/playground.spec.js` pins with `toHaveText(Object.keys(OPERATIONS))`;
appending keeps every existing option in its current position. Registered directly,
not via a lambda — `snake_case` takes only `text`, unlike `truncate`.

### Alternatives rejected

- **`slugify(text).replace("-", "_")`, in `web.py` or in `core.snake_case`.** Fewer
  lines, but it is wrong for input that already contains a hyphen-producing character
  run, it hides a text transformation behind a string patch, and it breaks silently if
  `slugify`'s separator ever changes. Rejected in the issue too.
- **A `separator=` parameter on `slugify`.** One function instead of two, but it changes
  a published signature and forces the playground to special-case an operation that
  takes an argument (the thing `truncate`'s lambda already demonstrates is awkward).
- **Duplicating the NFKD + `re.sub` body inside `snake_case`.** No new abstraction, but
  it is exactly the drift the issue asks to prevent: two copies of the accent and
  punctuation rules.
- **A dedicated `#snake-case` button, mirroring `#title-case`.** Rejected — see
  interpretation note 1 above.

## Components and data flow

| unit | interface | depends on |
| --- | --- | --- |
| `core._ascii_slug(text: str, separator: str) -> str` | private; NFKD-folds to ASCII, lowercases, replaces every run of non-`[a-z0-9]` with `separator`, strips leading/trailing `separator` | `re`, `unicodedata` |
| `core.slugify(text: str) -> str` | public, unchanged behaviour | `_ascii_slug(text, "-")` |
| `core.snake_case(text: str) -> str` | public, new | `_ascii_slug(text, "_")` |
| `textkit.__init__` | re-export | `core.snake_case` |
| `web.OPERATIONS["snake_case"]` | registry entry | `core.snake_case` |

Data flow for the page: browser `Apply` click → `applyOp("snake_case")` →
`POST /api/transform {"fn": "snake_case", "text": …}` → `handle_transform` →
`transform` → `OPERATIONS["snake_case"]` → `core.snake_case` → `200 {"result": …}` →
written into `#result`. No new code on any of those hops — the registration is the
whole change.

`core.py` must not import `web.py` (it does not today, and nothing here changes that).

### Behaviour table (these are the acceptance examples)

| input | `snake_case` | `slugify` (unchanged) |
| --- | --- | --- |
| `"Ada Lovelace"` | `"ada_lovelace"` | `"ada-lovelace"` |
| `"Café au lait"` | `"cafe_au_lait"` | `"cafe-au-lait"` |
| `""` | `""` | `""` |
| `"  Hello, World!!  "` | `"hello_world"` | `"hello-world"` |
| `"Ada Lovelace was a mathematician"` | `"ada_lovelace_was_a_mathematician"` | `"ada-lovelace-was-a-mathematician"` |
| `"Привет"` | `""` | `""` |
| `"Привет ada"` | `"ada"` | `"ada"` |
| `"kebab-case-text"` | `"kebab_case_text"` | `"kebab-case-text"` |
| `"__already__snake__"` | `"already_snake"` | `"already-snake"` |
| `"1.5 kg"` | `"1_5_kg"` | `"1-5-kg"` |

Consequences accepted deliberately: an input with no ASCII alphanumerics yields `""`
(not an error); digits are kept and never separated from adjacent letters
(`"utf8 text"` → `"utf8_text"`); there is no camelCase splitting, so
`"AdaLovelace"` → `"adalovelace"`.

## Error handling

`snake_case` is total: every `str` input returns a `str`, and it raises nothing. There
is no new failure mode to surface.

The existing error paths are untouched and must keep behaving exactly as they do now:
a non-string `fn`/`op`/`text`, malformed JSON, a non-object body, a missing field or an
unknown name still yield `400 {"error": …}`; an oversized body still yields `413`; an
unknown path still yields `404 {"error": "not found"}`. Because `snake_case` becomes a
*known* name, `{"fn": "snake_case"}` moves from the 400 branch to the 200 branch — that
is the only behavioural change on the HTTP surface.

Non-`str` input to `snake_case` (e.g. `None`) raises `TypeError` from
`unicodedata.normalize`, exactly as `slugify` does today. Not guarded, not tested — the
web layer already type-checks `text` before calling.

## Testing strategy

Three levels, all with the project's own runners.

1. **Unit, `tests/test_core.py`** — a `TestSnakeCase` class covering the behaviour table:
   the simple case, punctuation/whitespace collapsing, empty input, diacritics, non-Latin
   input, hyphen input, already-underscored input. Plus one parity test asserting
   `snake_case(s) == slugify(s).replace("-", "_")` over a fixed sample list — this is the
   regression guard for requirement 4 (shared logic), and it is a *test-only* expression,
   not the implementation.
2. **Unit, `tests/test_web.py`** — `transform("snake_case", SAMPLE) == core.snake_case(SAMPLE)`
   with the literal `"ada_lovelace_was_a_mathematician"` pinned once. Three existing tests
   pin the operation set literally and **must be updated**:
   `TestTransform.test_supported_ops`, `TestListTransforms.test_payload_shape`,
   `TestRenderPage.test_footer_counts_the_operations` (`6` → `7 operations`). The
   loop-driven tests (`test_every_op_returns_200`, `test_one_option_per_operation`,
   `test_every_listed_name_is_callable`, `test_derived_from_operations`) pick the new
   operation up with no edit.
3. **E2E, `e2e/tests/`** — a new `snake-case.spec.js` for the page and request-level
   scenario, plus updates to the four specs that hard-code the operation set:
   `playground.spec.js` (the `OPERATIONS` map, appended last), `footer.spec.js`
   (`FOOTER_TEXT`), `json-api.spec.js` (`NAMES`), `issue-19-consumer.spec.js` (the
   inline `transforms` list). `clear-button.spec.js` pins the buttons in `p:has(#apply)`
   as `["Apply", "Clear", "Title Case"]` and needs **no** change, because no button is
   added.

The Playwright suite is not installed in this sandbox; the plan carries the exact
install and run commands, and the unittest suite is the gate that must be green.

## Acceptance criteria

1. `from textkit import snake_case` works and `"snake_case"` is in `textkit.__all__`
   (alphabetically between `slugify` and `title_case`).
2. Every row of the behaviour table above holds, for both columns — in particular
   `snake_case("Café au lait") == "cafe_au_lait"` and `snake_case("") == ""`.
3. `textkit/core.py` contains exactly one NFKD-fold-and-collapse implementation:
   `grep -c 'unicodedata.normalize' textkit/core.py` is `1`, and both `slugify` and
   `snake_case` call `_ascii_slug`.
4. Every pre-existing assertion in `TestSlugify` still passes unmodified.
5. `sorted(OPERATIONS) == ["initials", "reverse_words", "shout", "slugify",
   "snake_case", "title_case", "truncate"]`, and `list(OPERATIONS)` ends with
   `["title_case", "snake_case"]` (insertion order = option order).
6. `GET /api/transforms` returns
   `{"transforms": ["initials", "reverse_words", "shout", "slugify", "snake_case",
   "title_case", "truncate"]}`.
7. `POST /api/transform` with `{"fn": "snake_case", "text": "Ada Lovelace"}` returns
   `200 {"result": "ada_lovelace"}`; the same body with `op` instead of `fn` returns
   the same thing.
8. `render_page()` contains `<option value="snake_case">snake_case</option>` and the
   footer reads `textkit playground · 7 operations`.
9. In the browser: type `Café au lait` in `#text`, select `snake_case` in `#op`, click
   `#apply` → `#result` shows `cafe_au_lait`.
10. Every existing operation still works under its existing name: `slugify`, `shout`,
    `initials`, `reverse_words`, `truncate`, `title_case` are unchanged in `OPERATIONS`,
    and no button, label or id on the page changes.
11. `python3 -m unittest discover -s tests -v` is green — 97 existing (three updated in
    place) + 10 new (9 in `TestSnakeCase`, 1 in `TestTransform`) = **107 tests**.
12. `CHANGELOG.md` gains exactly one new line at the end, in the `changelog` skill's
    format, in the same commit as the feature.
13. No `__pycache__/` or `*.pyc` is staged; the commit message starts with `[textkit] `.

## Main user scenario

1. Open `/`.
2. Type `Café au lait` into `#text`.
3. Choose `snake_case` in the `#op` select.
4. Click **Apply**.
5. `#result` shows `cafe_au_lait`.
6. Click **Clear** — `#text` empties, `#result` returns to the placeholder and `#op`
   still reads `snake_case`, exactly as for every other operation.

## Out of scope

- Any other new text operation.
- A dedicated `#snake-case` button, or any other change to the page's look, layout or
  styling. The new operation appears only as an `<option>`.
- A CLI entry point for `snake_case`.
- Changing `slugify`'s signature, its separator, or its behaviour in any way.
- camelCase/PascalCase word splitting, Unicode-aware casing beyond `str.lower()`, or a
  transliteration table for non-Latin scripts (they keep being dropped, as in `slugify`).
- Making `word_count` reachable from the playground.
- Any change to `handle_transform`, routing, `RESULT_PLACEHOLDER`, the char counter or
  Clear.
