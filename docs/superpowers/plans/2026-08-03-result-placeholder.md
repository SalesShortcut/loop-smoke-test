# playground result placeholder — implementation plan

Spec: `docs/superpowers/specs/2026-08-03-result-placeholder-design.md`
(source of truth; its Locked decisions are binding).

## Task 1: result placeholder

- [x] In `textkit/web.py` put the initial text `Nothing yet` inside the
  `<output id="result">` markup and make the `#clear` click handler set the
  result text back to `Nothing yet` instead of an empty string. No other
  markup or endpoint changes.
- [x] Update the page-markup unit tests in `tests/test_web.py`: the rendered
  page contains `Nothing yet` inside the result element; existing tests stay
  green. Fold the `CHANGELOG.md` entry into the same commit (changelog
  skill rule 4).
- [x] Run `python3 -m unittest discover -s tests -v` — green.

## Deviation from plan (recorded during execution)

The e2e specs `e2e/tests/playground.spec.js` and
`e2e/tests/clear-button.spec.js` were also updated, although this plan only
listed `textkit/web.py` and `tests/test_web.py`: their assertions expected an
empty `#result` after Clear, which contradicts the spec's locked decision
(Clear restores `Nothing yet`) and would have failed. The `applyOp` helper now
waits on the `/api/transform` response instead of on result-text inequality.
