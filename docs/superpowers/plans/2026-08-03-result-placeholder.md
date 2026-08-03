# playground result placeholder — implementation plan

Spec: `docs/superpowers/specs/2026-08-03-result-placeholder-design.md`
(source of truth; its Locked decisions are binding).

## Task 1: result placeholder

- [ ] In `textkit/web.py` put the initial text `Nothing yet` inside the
  `<output id="result">` markup and make the `#clear` click handler set the
  result text back to `Nothing yet` instead of an empty string. No other
  markup or endpoint changes.
- [ ] Update the page-markup unit tests in `tests/test_web.py`: the rendered
  page contains `Nothing yet` inside the result element; existing tests stay
  green. Fold the `CHANGELOG.md` entry into the same commit (changelog
  skill rule 4).
- [ ] Run `python3 -m unittest discover -s tests -v` — green.
