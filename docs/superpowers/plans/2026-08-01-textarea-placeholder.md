# playground textarea placeholder — implementation plan

Spec: `docs/superpowers/specs/2026-08-01-textarea-placeholder-design.md`
(source of truth; its Locked decisions are binding).

## Task 1: placeholder

- [ ] In `textkit/web.py` add `placeholder="Type your text…"` to the
  `<textarea id="text">` markup. No other markup or endpoint changes.
- [ ] Update the page-markup unit tests in `tests/test_web.py`: the rendered
  page contains the placeholder string; existing tests stay green. Fold the
  `CHANGELOG.md` entry into the same commit (changelog skill rule 4).
- [ ] Run `python3 -m unittest discover -s tests -v` — green.
