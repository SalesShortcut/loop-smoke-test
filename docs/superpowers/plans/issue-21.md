# snake_case Transform Implementation Plan

> **For agentic workers:** implement this plan task by task, in order. Steps use checkbox
> (`- [ ]`) syntax — tick them off in this file as you go. If the `parallel-plan-execution`
> skill is available and the tasks split into file-disjoint streams, use it.

**Goal:** Add a pure `snake_case(text)` function to `textkit` and register it in the web
playground's `OPERATIONS` registry, so it is reachable from the page's `#op` select and from
`POST /api/transform`.

**Architecture:** `slugify`'s NFKD-fold-lowercase-collapse body is extracted into a private
`_ascii_slug(text, separator)` helper in `textkit/core.py`; `slugify` calls it with `"-"` and the
new `snake_case` calls it with `"_"`, so the two can never drift. `textkit/web.py` gains one
`OPERATIONS` entry — that single registration feeds the `<select>` options, the footer count,
`GET /api/transforms` and `POST /api/transform` at once. No new UI element is added.

**Tech Stack:** Python 3 standard library only (`re`, `unicodedata`, `http.server`), `unittest`
for unit tests, Playwright (`@playwright/test`) for e2e.

Spec: `docs/superpowers/specs/issue-21-design.md` — source of truth; its locked decisions
(no new button; append `snake_case` last in `OPERATIONS`) are binding.
Issue: #21 (`.loop/task.md`)

Everything lands in **one commit**, created in Task 7. Earlier tasks leave the working tree
green but uncommitted. The commit message must start with `[textkit] ` (`CLAUDE.md`).

---

## File Structure

| file | responsibility | change |
| --- | --- | --- |
| `textkit/core.py` | pure text functions | add `_ascii_slug`, rewrite `slugify`'s body, add `snake_case` |
| `textkit/__init__.py` | public re-exports | add `snake_case` to the import block and `__all__` |
| `textkit/web.py` | playground page + JSON API | add one `OPERATIONS` entry |
| `tests/test_core.py` | core unit tests | add `TestSnakeCase` (8 tests) |
| `tests/test_web.py` | web unit tests | add 1 test; update 3 that pin the operation set |
| `e2e/tests/snake-case.spec.js` | e2e for the new operation | **create** |
| `e2e/tests/playground.spec.js` | e2e op matrix | append `snake_case` to the `OPERATIONS` map |
| `e2e/tests/footer.spec.js` | e2e footer text | `6` → `7 operations` |
| `e2e/tests/json-api.spec.js` | e2e API list | add `"snake_case"` to `NAMES` |
| `e2e/tests/issue-19-consumer.spec.js` | e2e consumer walkthrough | add `"snake_case"` to the inline list |
| `CHANGELOG.md` | changelog | one appended line |

`e2e/tests/clear-button.spec.js`, `char-counter.spec.js`, `result-placeholder.spec.js` and
`title-case.spec.js` need **no** change — no button is added and no existing behaviour moves.

---

## Task 1: `_ascii_slug` helper + `snake_case` in the library

**Files:**
- Modify: `textkit/core.py`
- Test: `tests/test_core.py`

- [x] **Step 1: Write the failing test**

In `tests/test_core.py`, add `snake_case` to the existing `from textkit import (...)` block
(alphabetically, between `shout` and `slugify` — the block is sorted, so the result is
`initials, reverse_words, shout, slugify, snake_case, title_case, truncate, word_count`).

Then add this class immediately after `class TestSlugify`:

```python
class TestSnakeCase(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(snake_case("Ada Lovelace"), "ada_lovelace")

    def test_punctuation_collapses(self):
        self.assertEqual(snake_case("  Hello, World!!  "), "hello_world")

    def test_empty(self):
        self.assertEqual(snake_case(""), "")

    def test_diacritics_reduce_to_ascii(self):
        self.assertEqual(snake_case("Café au lait"), "cafe_au_lait")

    def test_non_latin_scripts_are_dropped(self):
        self.assertEqual(snake_case("Привет"), "")
        self.assertEqual(snake_case("Привет ada"), "ada")

    def test_hyphens_become_underscores(self):
        self.assertEqual(snake_case("kebab-case-text"), "kebab_case_text")

    def test_repeated_underscores_collapse_and_strip(self):
        self.assertEqual(snake_case("__already__snake__"), "already_snake")

    def test_digits_are_kept(self):
        self.assertEqual(snake_case("1.5 kg"), "1_5_kg")

    def test_shares_slugify_normalisation(self):
        # Requirement 4 of the spec: the ASCII folding and collapsing logic is
        # shared, so the two functions differ only in the separator.
        for text in (
            "Ada Lovelace",
            "Café au lait",
            "  Hello, World!!  ",
            "Привет ada",
            "1.5 kg",
            "",
        ):
            with self.subTest(text=text):
                self.assertEqual(snake_case(text), slugify(text).replace("-", "_"))
```

That is 9 test methods. `test_non_latin_scripts_are_dropped` makes two assertions and
`test_shares_slugify_normalisation` uses `subTest`, but each still counts as one test, so
`TestSnakeCase` contributes 9 to the suite total (97 baseline → 106 after this task).

- [x] **Step 2: Run the tests to verify they fail**

Run: `python3 -m unittest discover -s tests -v 2>&1 | tail -5`
Expected: FAIL — `ImportError: cannot import name 'snake_case' from 'textkit'`.

- [x] **Step 3: Write the implementation**

In `textkit/core.py`, replace the whole existing `slugify` function with the helper plus the
two public functions. The `_ascii_slug` helper goes directly above `slugify`; `snake_case`
goes directly below it.

```python
def _ascii_slug(text: str, separator: str) -> str:
    """Fold text to lowercase ASCII, joining the surviving runs with separator.

    Shared by slugify and snake_case so the two agree on accents and
    punctuation; the separator is the only difference between them.
    """
    ascii_text = (
        unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    )
    return re.sub(r"[^a-z0-9]+", separator, ascii_text.lower()).strip(separator)


def slugify(text: str) -> str:
    """Return a URL-safe ASCII slug built from text.

    Accented Latin letters are reduced to their base letter (NFKD), then
    ASCII letters and digits are kept and lowercased; every other run of
    characters — including non-Latin scripts — becomes a single hyphen.

    Example:
        >>> slugify("Ada Lovelace")
        'ada-lovelace'
        >>> slugify("Café au lait")
        'cafe-au-lait'
    """
    return _ascii_slug(text, "-")


def snake_case(text: str) -> str:
    """Return text as a snake_case ASCII identifier.

    Normalisation is identical to slugify — NFKD-fold to ASCII, lowercase,
    collapse every run of other characters — but the separator is "_", and
    leading and trailing separators are stripped.

    Example:
        >>> snake_case("Ada Lovelace")
        'ada_lovelace'
        >>> snake_case("Café au lait")
        'cafe_au_lait'
    """
    return _ascii_slug(text, "_")
```

`slugify`'s docstring is copied over verbatim from the current file — do not reword it. No new
imports: `re` and `unicodedata` are already imported at the top of `core.py`. The `Example:`
section in `snake_case`'s docstring is mandatory per `CLAUDE.md`.

- [x] **Step 4: Export the new function**

In `textkit/__init__.py`, add `snake_case` to both lists, between `slugify` and `title_case`:

```python
from .core import (
    initials,
    reverse_words,
    shout,
    slugify,
    snake_case,
    title_case,
    truncate,
    word_count,
)

__all__ = [
    "initials",
    "reverse_words",
    "shout",
    "slugify",
    "snake_case",
    "title_case",
    "truncate",
    "word_count",
]
```

- [x] **Step 5: Run the tests to verify they pass**

Run: `python3 -m unittest discover -s tests -v 2>&1 | tail -5`
Expected: `Ran 106 tests` … `OK`. (Baseline before this plan is 97; Task 2 adds the 107th.)

If `TestSlugify` fails here, `_ascii_slug` was transcribed wrongly — the regex is
`r"[^a-z0-9]+"` applied to `ascii_text.lower()`, and `.strip(separator)` comes last.

---

## Task 2: register the operation in the playground

**Files:**
- Modify: `textkit/web.py` (the `OPERATIONS` dict)
- Test: `tests/test_web.py`

- [x] **Step 1: Write the failing test**

In `tests/test_web.py`, add this method to `class TestTransform`, immediately after
`test_title_case_matches_core`:

```python
    def test_snake_case_matches_core(self):
        self.assertEqual(transform("snake_case", SAMPLE), core.snake_case(SAMPLE))
        self.assertEqual(
            transform("snake_case", SAMPLE), "ada_lovelace_was_a_mathematician"
        )
```

- [x] **Step 2: Run it to verify it fails**

Run: `python3 -m unittest tests.test_web.TestTransform.test_snake_case_matches_core -v`
Expected: FAIL — `ValueError: unknown op: 'snake_case'`.

- [x] **Step 3: Write the implementation**

In `textkit/web.py`, append one entry to `OPERATIONS`, **after** `title_case` (dict order is
the `<select>` option order; appending leaves every existing option where it is):

```python
OPERATIONS = {
    "slugify": core.slugify,
    "shout": core.shout,
    "initials": core.initials,
    "reverse_words": core.reverse_words,
    "truncate": lambda text: core.truncate(text, TRUNCATE_WIDTH),
    "title_case": core.title_case,
    "snake_case": core.snake_case,
}
```

Registered directly, not through a lambda — `snake_case` takes only `text`. Nothing else in
`web.py` changes: no edit to `render_page`, `handle_transform`, `list_transforms` or the
handler class.

- [x] **Step 4: Run it to verify it passes**

Run: `python3 -m unittest tests.test_web.TestTransform.test_snake_case_matches_core -v`
Expected: `OK`.

---

## Task 3: update the unit tests that pin the operation set

**Files:**
- Modify: `tests/test_web.py`

Three existing tests hard-code the six operations and now fail. Fix each one.

- [x] **Step 1: Run the suite to see exactly which tests broke**

Run: `python3 -m unittest discover -s tests 2>&1 | tail -20`
Expected: 3 failures — `test_supported_ops`, `test_payload_shape`,
`test_footer_counts_the_operations`.

- [x] **Step 2: Update `TestTransform.test_supported_ops`**

The expected list is `sorted(...)`, so `snake_case` goes between `slugify` and `title_case`:

```python
    def test_supported_ops(self):
        self.assertEqual(
            sorted(OPERATIONS),
            [
                "initials",
                "reverse_words",
                "shout",
                "slugify",
                "snake_case",
                "title_case",
                "truncate",
            ],
        )
```

- [x] **Step 3: Update `TestListTransforms.test_payload_shape`**

```python
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
                    "snake_case",
                    "title_case",
                    "truncate",
                ]
            },
        )
```

- [x] **Step 4: Update `TestRenderPage.test_footer_counts_the_operations`**

The footer is generated from `len(OPERATIONS)`, which is now 7:

```python
    def test_footer_counts_the_operations(self):
        # The literal count is pinned by the plan; test_supported_ops already
        # pins the operation set itself.
        self.assertIn(
            '<footer id="footer">textkit playground · 7 operations</footer>',
            self.page,
        )
```

Keep the `·` character exactly as it is in the file (U+00B7 middle dot, surrounded by
ordinary spaces).

- [x] **Step 5: Run the full suite**

Run: `python3 -m unittest discover -s tests -v 2>&1 | tail -5`
Expected: `Ran 107 tests` … `OK` (97 baseline + 9 from Task 1 + 1 from Task 2).

Do **not** touch `test_every_op_returns_200`, `test_one_option_per_operation`,
`test_derived_from_operations` or `test_every_listed_name_is_callable` — they iterate
`OPERATIONS` and already cover the new operation.

---

## Task 4: update the e2e specs that pin the operation set

**Files:**
- Modify: `e2e/tests/playground.spec.js`, `e2e/tests/footer.spec.js`,
  `e2e/tests/json-api.spec.js`, `e2e/tests/issue-19-consumer.spec.js`

These four files hard-code the six operations. Playwright is not installed in this sandbox
(there is no `e2e/node_modules`), so the edits are made now and verified in Task 6.

- [x] **Step 1: `e2e/tests/playground.spec.js` — append to the `OPERATIONS` map**

The map's key order is asserted against the rendered option order
(`toHaveText(Object.keys(OPERATIONS))`), so `snake_case` must be **last**, matching the dict
order in `web.py`:

```javascript
const OPERATIONS = {
  slugify: "ada-lovelace-was-a-mathematician",
  shout: "ADA LOVELACE WAS A MATHEMATICIAN",
  initials: "A.L.W.A.M.",
  reverse_words: "mathematician a was Lovelace Ada",
  truncate: "Ada Lovelace was...",
  title_case: "Ada Lovelace Was a Mathematician",
  snake_case: "ada_lovelace_was_a_mathematician",
};
```

The `critical paths` loop below it then covers the new operation with no further edit.

- [x] **Step 2: `e2e/tests/footer.spec.js` — bump the count**

```javascript
// Locked decision: exact text with a middle-dot separator, N = 7 operations.
const FOOTER_TEXT = "textkit playground · 7 operations";
```

- [x] **Step 3: `e2e/tests/json-api.spec.js` — extend `NAMES`**

This list is compared with the sorted `GET /api/transforms` payload, so `snake_case` goes
between `slugify` and `title_case`:

```javascript
const NAMES = [
  "initials",
  "reverse_words",
  "shout",
  "slugify",
  "snake_case",
  "title_case",
  "truncate",
];
```

- [x] **Step 4: `e2e/tests/issue-19-consumer.spec.js` — extend the inline list**

Inside `test("discover transforms, apply title_case, get a friendly error on a typo", ...)`:

```javascript
    expect(transforms).toEqual([
      "initials",
      "reverse_words",
      "shout",
      "slugify",
      "snake_case",
      "title_case",
      "truncate",
    ]);
```

- [x] **Step 5: Confirm nothing else pins the set**

Run: `grep -rn "reverse_words" e2e/tests/`
Expected: hits only in `playground.spec.js`, `json-api.spec.js` and
`issue-19-consumer.spec.js` — the three files just edited. `clear-button.spec.js` pins
`["Apply", "Clear", "Title Case"]`, which is unaffected because this change adds no button.

---

## Task 5: new e2e spec for `snake_case`

**Files:**
- Create: `e2e/tests/snake-case.spec.js`

- [ ] **Step 1: Write the spec file**

```javascript
// E2E scenarios for the playground snake_case operation.
// Spec: docs/superpowers/specs/issue-21-design.md
const { test, expect } = require("@playwright/test");
const { PLACEHOLDER } = require("./constants");

async function applyOp(page, op, text) {
  await page.fill("#text", text);
  await page.selectOption("#op", op);
  // Wait on the transform request itself, as the other specs do.
  const responded = page.waitForResponse("**/api/transform");
  await page.click("#apply");
  await responded;
}

test.describe("snake_case — main user scenario", () => {
  test("selecting snake_case and pressing Apply fills #result", async ({
    page,
  }) => {
    await page.goto("/");
    await applyOp(page, "snake_case", "Café au lait");
    await expect(page.locator("#result")).toHaveText("cafe_au_lait");
  });
});

test.describe("snake_case — critical paths", () => {
  test("the operation is offered as the last option in #op", async ({
    page,
  }) => {
    await page.goto("/");
    const option = page.locator('#op option[value="snake_case"]');
    await expect(option).toHaveCount(1);
    await expect(option).toHaveText("snake_case");
    const values = await page
      .locator("#op option")
      .evaluateAll((options) => options.map((option) => option.value));
    expect(values[values.length - 1]).toBe("snake_case");
  });

  test("no snake_case button was added to the action row", async ({ page }) => {
    // Locked decision: the operation lives in the select only.
    await page.goto("/");
    await expect(page.locator("p:has(#apply) button")).toHaveText([
      "Apply",
      "Clear",
      "Title Case",
    ]);
  });

  test("slugify and snake_case differ only in the separator", async ({
    page,
  }) => {
    await page.goto("/");
    await applyOp(page, "slugify", "Café au lait");
    await expect(page.locator("#result")).toHaveText("cafe-au-lait");
    await applyOp(page, "snake_case", "Café au lait");
    await expect(page.locator("#result")).toHaveText("cafe_au_lait");
  });

  test("Clear still works after a snake_case run", async ({ page }) => {
    await page.goto("/");
    await applyOp(page, "snake_case", "Ada Lovelace");
    await expect(page.locator("#result")).toHaveText("ada_lovelace");

    await page.click("#clear");
    await expect(page.locator("#text")).toHaveValue("");
    await expect(page.locator("#result")).toHaveText(PLACEHOLDER);
    await expect(page.locator("#op")).toHaveValue("snake_case");
  });
});

test.describe("snake_case — API critical paths (request-level)", () => {
  test("POST /api/transform with fn returns the snake_case result", async ({
    request,
  }) => {
    const response = await request.post("/api/transform", {
      data: { fn: "snake_case", text: "Ada Lovelace" },
    });
    expect(response.status()).toBe(200);
    expect(await response.json()).toEqual({ result: "ada_lovelace" });
  });

  test("the legacy op field still works for the new name", async ({
    request,
  }) => {
    const response = await request.post("/api/transform", {
      data: { op: "snake_case", text: "Ada Lovelace" },
    });
    expect(response.status()).toBe(200);
    expect(await response.json()).toEqual({ result: "ada_lovelace" });
  });

  test("GET /api/transforms advertises snake_case", async ({ request }) => {
    const { transforms } = await (await request.get("/api/transforms")).json();
    expect(transforms).toContain("snake_case");
  });
});
```

- [ ] **Step 2: Sanity-check the file parses**

Run: `node --check e2e/tests/snake-case.spec.js`
Expected: no output, exit status 0. (If `node` is unavailable, skip this step — Task 6
catches syntax errors.)

---

## Task 6: verification

**Files:** none modified.

- [ ] **Step 1: Full unit suite**

Run: `python3 -m unittest discover -s tests -v 2>&1 | tail -5`
Expected: `Ran 107 tests` … `OK`.

- [ ] **Step 2: Confirm the normalisation is shared, not duplicated**

Run: `grep -c 'unicodedata.normalize' textkit/core.py`
Expected: `1`.

- [ ] **Step 3: Start the server and check the HTTP surface**

```bash
TEXTKIT_PORT=3000 python3 -m textkit.web &
sleep 1
curl -s 127.0.0.1:3000/api/transforms
curl -s -X POST 127.0.0.1:3000/api/transform -d '{"fn":"snake_case","text":"Ada Lovelace"}'
curl -s -X POST 127.0.0.1:3000/api/transform -d '{"op":"snake_case","text":"Café au lait"}'
curl -s -X POST 127.0.0.1:3000/api/transform -d '{"fn":"slugify","text":"Ada Lovelace"}'
curl -s 127.0.0.1:3000/ | grep -E 'snake_case|7 operations'
```

Expected, in order:
```
{"transforms": ["initials", "reverse_words", "shout", "slugify", "snake_case", "title_case", "truncate"]}
{"result": "ada_lovelace"}
{"result": "cafe_au_lait"}
{"result": "ada-lovelace"}
        <option value="snake_case">snake_case</option>
  <footer id="footer">textkit playground · 7 operations</footer>
```

Stop the server afterwards (`kill %1`).

- [ ] **Step 4: Playwright suite (best effort)**

The suite is not installed in this sandbox. With the server from Step 3 still running on
port 3000:

```bash
cd e2e
npm ci
PLAYWRIGHT_BROWSERS_PATH=/home/sandbox/.cache/ms-playwright npx playwright install chromium
PLAYWRIGHT_BROWSERS_PATH=/home/sandbox/.cache/ms-playwright \
  E2E_BASE_URL=http://localhost:3000 npx playwright test
```

Expected: all specs pass, including the 8 new ones in `snake-case.spec.js`. The default
browser path `/opt/pw-browsers` is read-only and `--with-deps` needs root — hence the
`PLAYWRIGHT_BROWSERS_PATH` override. If `npm ci` or the browser download cannot reach the
network, record that the e2e run was skipped and rely on Steps 1–3; do **not** revert the
e2e edits from Tasks 4 and 5.

---

## Task 7: changelog and commit

**Files:**
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Append the changelog entry**

Per the `changelog` skill (`.claude/skills/changelog/SKILL.md`): one line, appended to the
**end** of `CHANGELOG.md`, format `- YYYY-MM-DD: <имя функции> — <описание на русском>`:

```
- 2026-08-04: snake_case — идентификатор в snake_case из произвольной строки
```

Use the actual current UTC date if it has moved past 2026-08-04. Do not add a heading, a
blank line or a second entry.

- [ ] **Step 2: Check nothing forbidden is about to be staged**

Run: `git status --porcelain`
Expected: only the files in the File Structure table above. No `__pycache__/`, no `*.pyc`
(they are in `.gitignore` — do not force-add them).

- [ ] **Step 3: Commit**

```bash
git add textkit/core.py textkit/__init__.py textkit/web.py \
        tests/test_core.py tests/test_web.py \
        e2e/tests/snake-case.spec.js e2e/tests/playground.spec.js \
        e2e/tests/footer.spec.js e2e/tests/json-api.spec.js \
        e2e/tests/issue-19-consumer.spec.js \
        CHANGELOG.md
git commit -m "[textkit] feat: snake_case — операция snake_case в core и плейграунде"
```

The `[textkit] ` prefix is mandatory (`CLAUDE.md`). Do **not** `git push` and do **not**
switch branches.

- [ ] **Step 4: Confirm the commit**

Run: `git show --stat HEAD`
Expected: 11 files changed, message starting with `[textkit] `.

---

## Risks / watch-outs

- **Four separate places pin the operation count or set** — `test_supported_ops`,
  `test_payload_shape`, `test_footer_counts_the_operations` (unit) and `footer.spec.js`,
  `json-api.spec.js`, `issue-19-consumer.spec.js`, `playground.spec.js` (e2e). Missing one is
  the most likely cause of a red suite. Task 3 Step 1 flushes the unit ones out; Task 4 Step 5
  flushes the e2e ones out.
- **Insertion order matters.** `snake_case` must be the **last** key in `OPERATIONS` and the
  **last** key in `playground.spec.js`'s `OPERATIONS` map, but it sorts between `slugify` and
  `title_case` in every `sorted()`-derived list. These two orders are different on purpose.
- **Do not implement `snake_case` as `slugify(text).replace("-", "_")`.** That expression
  appears only inside `test_shares_slugify_normalisation` as an independent oracle; using it as
  the implementation would make that test vacuous and violates spec requirement 4.
- `render_page` is one large f-string. This change touches no part of it, so no brace
  doubling is involved — if you find yourself editing the f-string, you have gone off-plan.
- `textkit/core.py` must not import `textkit/web.py`. `_ascii_slug` is private (leading
  underscore) and is deliberately **not** added to `textkit/__init__.py` or `__all__`.
