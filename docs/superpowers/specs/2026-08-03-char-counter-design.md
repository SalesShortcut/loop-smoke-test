# playground character counter — design

Date: 2026-08-03
Status: approved

## What we are building

A live character counter under the playground's input field: the page always
shows how many characters are currently typed, so users see input size at a
glance.

## Locked decisions

- A `<div id="charcount">` sits directly below `<textarea id="text">`;
  its initial text is `0 characters`.
- On every `input` event of the textarea the element text becomes
  `N characters`, where N is the current length of the textarea value
  (exact format: number, one space, the word `characters`).
- Clicking `#clear` resets the counter to `0 characters`.
- Implementation is plain inline JavaScript in the page markup produced by
  `textkit/web.py`; no new endpoints, no external assets.
- Everything else on the page stays exactly as specified in
  `docs/superpowers/specs/2026-08-01-web-playground-design.md`,
  `docs/superpowers/specs/2026-08-01-clear-button-design.md` and
  `docs/superpowers/specs/2026-08-01-textarea-placeholder-design.md`.

## Main user scenario

1. Open `/` — the counter under the textarea shows `0 characters`.
2. Type `Ada` — the counter shows `3 characters`.
3. Click `#clear` — the textarea empties and the counter shows `0 characters`.

## Out of scope

Word counts, styling, localisation, counters for the output area.
