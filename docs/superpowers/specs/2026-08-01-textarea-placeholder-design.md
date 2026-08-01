# playground textarea placeholder — design

Date: 2026-08-01
Status: approved

## What we are building

A placeholder hint in the playground's input field so an empty page explains
itself: the `<textarea id="text">` shows `Type your text…` until the user
starts typing.

## Locked decisions

- `<textarea id="text">` gets the attribute `placeholder="Type your text…"`
  (exact string, with the `…` ellipsis character) in `textkit/web.py`.
- Nothing else on the page changes: elements, ids, title, the Clear button
  and `/api/transform` stay exactly as specified in
  `docs/superpowers/specs/2026-08-01-web-playground-design.md` and
  `docs/superpowers/specs/2026-08-01-clear-button-design.md`.

## Main user scenario

1. Open `/` — the empty textarea shows the hint `Type your text…`.
2. Type any text — the hint disappears (native browser behaviour); the
   playground works as before.
3. Click `#clear` — the textarea empties and the hint is visible again.

## Out of scope

Styling, localisation, placeholders on other elements.
