# playground result placeholder — design

Date: 2026-08-03
Status: approved

## What we are building

A placeholder in the playground's result area so the page never shows an
empty output: until the first transform the `<output id="result">` element
displays `Nothing yet`.

## Locked decisions

- `<output id="result">` initially contains the text `Nothing yet`
  (exact string) in the markup produced by `textkit/web.py`.
- A successful Apply replaces it with the transform result, as today.
- Clicking `#clear` restores the text `Nothing yet` (instead of emptying
  the element).
- Plain inline JavaScript / markup changes only; no new endpoints,
  no external assets.
- Everything else on the page stays exactly as specified in the previous
  playground specs (web-playground, clear-button, textarea-placeholder,
  char-counter).

## Main user scenario

1. Open `/` — the result area shows `Nothing yet`.
2. Type `Ada Lovelace`, pick `slugify`, press Apply — the result area shows
   `ada-lovelace`.
3. Press `#clear` — the textarea empties, the counter resets and the result
   area shows `Nothing yet` again.

## Out of scope

Styling, localisation, placeholders anywhere else, error-message wording.

## Revision 2026-08-03: placeholder text overridden by reviewer feedback

A human reviewer of the staged result requested the placeholder text
`Type something and press Apply Beza`. This supersedes the locked decision
above that fixed the string as `Nothing yet`; every other decision stands
unchanged. The string was implemented verbatim as quoted in the feedback,
including the trailing word «Beza», which has not yet been confirmed with
the reviewer and may be a typo. If it turns out to be unintended, the only
places to change are the `RESULT_PLACEHOLDER` constant in `textkit/web.py`,
its literal pin in `tests/test_web.py`
(`test_result_starts_with_the_placeholder`) and the shared `PLACEHOLDER`
constant in `e2e/tests/constants.js`.
