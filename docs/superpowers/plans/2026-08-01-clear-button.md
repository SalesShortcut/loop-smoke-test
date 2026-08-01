# playground Clear button — implementation plan

Spec: `docs/superpowers/specs/2026-08-01-clear-button-design.md` (source of
truth; its Locked decisions are binding).

## Task 1: Clear button

- [x] In `textkit/web.py` add `<button id="clear">Clear</button>` next to
  `#apply` in the page markup, and inline JS: on click set `#text` value and
  `#result` textContent to empty strings. No new endpoints.
- [x] Update the page-markup unit tests in `tests/test_web.py`: the rendered
  page contains `id="clear"`; existing tests stay green. Fold the
  `CHANGELOG.md` entry into the same commit (changelog skill rule 4).
- [x] Run `python3 -m unittest discover -s tests -v` — green.
