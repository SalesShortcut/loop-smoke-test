# playground Clear button — design

Date: 2026-08-01
Status: approved

## What we are building

A **Clear** button on the textkit playground page that resets the form: it
empties the input text and the shown result in one click.

## Locked decisions

- A `<button id="clear">` labelled `Clear` on the playground page
  (`textkit/web.py`, `GET /`), rendered next to the existing
  `<button id="apply">`.
- Clicking `#clear` sets the value of `<textarea id="text">` to an empty
  string and the content of `<output id="result">` to an empty string.
  Client-side only — no new HTTP endpoints, no server round-trip.
- The `<select id="op">` selection is left untouched by the button.
- Everything else about the page (elements, ids, title, `/api/transform`)
  stays exactly as specified in
  `docs/superpowers/specs/2026-08-01-web-playground-design.md`.

## Main user scenario

1. Open `/`, type `Ada Lovelace` into `#text`, select `slugify`, click
   `#apply` — `#result` shows `ada-lovelace`.
2. Click `#clear` — both `#text` and `#result` become empty; the `slugify`
   option stays selected.

## Out of scope

Keyboard shortcuts, confirmation dialogs, styling.
