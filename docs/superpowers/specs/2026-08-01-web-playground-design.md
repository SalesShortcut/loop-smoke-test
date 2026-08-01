# textkit web playground — design

Date: 2026-08-01
Status: approved

## What we are building

A tiny web playground for textkit: a single HTML page where a user types text,
picks a transformation, clicks **Apply** and sees the result. Standard library
only (`http.server`) — no new dependencies.

## Locked decisions

- Module `textkit/web.py`, started with `python3 -m textkit.web`.
- Port comes from the `TEXTKIT_PORT` environment variable, default `3000`;
  bind to `0.0.0.0`.
- `GET /` returns the playground page (HTML with inline JS, no external
  assets).
- `POST /api/transform` accepts JSON `{"op": str, "text": str}` and returns
  JSON `{"result": str}`. Unknown `op` or malformed body → HTTP 400 with JSON
  `{"error": str}`.
- Supported operations (must map to the existing functions in
  `textkit/core.py`): `slugify`, `shout`, `initials`, `reverse_words`,
  `truncate` (truncate uses width 20 in the playground).
- The page must contain exactly these elements (stable ids for testing):
  - `<textarea id="text">` — input text
  - `<select id="op">` — one `<option>` per operation, value = op name
  - `<button id="apply">` — sends the request
  - `<output id="result">` — shows `result` (or the error message) after the
    response arrives
- The page title is `textkit playground`.

## Main user scenario

1. Open `/` — the page shows the four elements above.
2. Type `Ada Lovelace` into `#text`, select `slugify`, click `#apply`.
3. `#result` shows `ada-lovelace`.

Critical paths: each of the five operations returns the same value as the
corresponding `textkit.core` function; an unknown op surfaces the error
message in `#result` and does not crash the server.

## Out of scope

Styling, persistence, concurrency tuning, HTTPS.
