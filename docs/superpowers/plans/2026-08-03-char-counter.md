# playground character counter — implementation plan

Spec: `docs/superpowers/specs/2026-08-03-char-counter-design.md`
(source of truth; its Locked decisions are binding).

## Task 1: counter element and script

- [ ] In `textkit/web.py` add `<div id="charcount">0 characters</div>`
  directly below the `<textarea id="text">` markup and an inline `<script>`
  that updates the counter on the textarea `input` event and resets it when
  `#clear` is clicked. No other markup or endpoint changes.
- [ ] Update the page-markup unit tests in `tests/test_web.py`: the rendered
  page contains `id="charcount"` and the initial `0 characters`; existing
  tests stay green. Fold the `CHANGELOG.md` entry into the same commit
  (changelog skill rule 4).
- [ ] Run `python3 -m unittest discover -s tests -v` — green.
