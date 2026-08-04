# Issue #21: Add a snake_case operation to textkit and the playground

Labels: loop:ready, loop:lane:textkit

## Goal

Add a `snake_case` text operation to textkit and expose it in the web playground, so a user can
turn a phrase into a snake_case identifier the same way they already can with `slugify`.

## Context

- Where this lives: `textkit/core.py` (the pure functions), `textkit/web.py` (the playground page
  and the JSON API), `tests/test_core.py`, `tests/test_web.py`, `e2e/tests/`.
- Current behavior: `textkit/core.py` exposes `word_count`, `slugify`, `shout`, `initials`,
  `reverse_words`, `truncate` and `title_case`. `textkit/web.py` wires a subset of them into the
  `OPERATIONS` dict, which drives both the operation buttons on the page and the `op` field of the
  JSON API. There is no way to produce a snake_case identifier: `slugify` returns hyphens.
- Constraints: `snake_case` must be a pure function in `core.py` with no import of `web.py`; the
  existing operations, their button labels and their JSON `op` names must not change.

## Approach

Implement `snake_case` in `core.py` by reusing the same normalisation `slugify` already performs —
NFKD-fold to ASCII, lowercase, collapse every other run of characters into a single separator — with
`_` as the separator instead of `-`. Factor the shared normalisation into a private helper that both
functions call, so the two can never drift apart in how they treat accents or punctuation.

Then register `"snake_case": core.snake_case` in `OPERATIONS` in `web.py`. Because the page's buttons
and the JSON API both read that dict, one registration covers both surfaces.

Alternatives considered and rejected:

- `slugify(text).replace("-", "_")` in `web.py` — no new core function, but it puts a text
  transformation in the web layer where it cannot be unit-tested on its own, and it silently breaks
  if `slugify`'s separator ever changes.
- A `separator` parameter on `slugify` — fewer functions, but it changes an existing public
  signature and makes the playground pass an argument that no other operation takes.

## Requirements

1. `core.snake_case(text)` returns the text folded to ASCII, lowercased, with every run of
   non-alphanumeric characters replaced by a single `_` and no leading or trailing `_`.
2. `core.snake_case("Café au lait")` returns `"cafe_au_lait"`.
3. `core.snake_case("")` returns `""`.
4. The ASCII-folding and collapsing logic is shared with `slugify` rather than duplicated, and
   `slugify`'s existing behavior is unchanged.
5. `web.OPERATIONS` gains a `"snake_case"` entry, which makes the button appear on the page and
   `{"op": "snake_case"}` work in the JSON API.
6. Unit tests cover `snake_case` in `tests/test_core.py` and its exposure through the API in
   `tests/test_web.py`.

## Acceptance criteria

- [ ] `python3 -m unittest discover -s tests -v` passes, including the new tests.
- [ ] `POST /` with `{"op": "snake_case", "text": "Ada Lovelace"}` returns `"ada_lovelace"`.
- [ ] The playground page shows a `snake_case` button alongside the existing operations, and
      pressing it with `Café au lait` in the input shows `cafe_au_lait` in the result area.
- [ ] Every existing operation still works and its JSON `op` name is unchanged.

## Verification

```
python3 -m unittest discover -s tests -v      # test command from .loop.yml
python3 -m textkit.web                        # run command from .loop.yml, serves TEXTKIT_PORT (3000)
```

## Out of scope

- Any other new text operation.
- Changing the look of the playground beyond the one new button.
- A CLI entry point for the new function.

## Notes for the planner

`OPERATIONS` in `textkit/web.py` is the single registry behind both the rendered buttons and the
JSON API, so the button and the API endpoint are one change, not two. `truncate` is registered there
as a lambda because it takes a width; `snake_case` takes only the text and should be registered
directly. `RESULT_PLACEHOLDER` and the existing e2e specs under `e2e/tests/` show the selectors the
page uses — follow them rather than inventing new ones.

