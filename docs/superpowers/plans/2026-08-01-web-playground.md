# textkit web playground — implementation plan

Spec: `docs/superpowers/specs/2026-08-01-web-playground-design.md` (source of
truth; its Locked decisions are binding).

## Task 1: transform dispatch

- [x] Add `textkit/web.py` with a pure function
  `transform(op: str, text: str) -> str` mapping op names to
  `textkit.core` functions per the spec (`truncate` with width 20).
  Unknown op raises `ValueError`. Docstring with an `Example:` block per
  repository conventions.
- [x] Unit tests in `tests/test_web.py` (unittest): every supported op
  matches its `textkit.core` counterpart; unknown op raises `ValueError`.
- [x] Run `python3 -m unittest discover -s tests -v` — green.

## Task 2: HTTP server and page

- [x] In `textkit/web.py` add a `BaseHTTPRequestHandler`-based server:
  `GET /` serves the playground HTML (elements and ids exactly per spec,
  inline JS calling `POST /api/transform` via fetch and writing `result`
  or the error message into `#result`); `POST /api/transform` parses JSON,
  calls `transform`, returns `{"result": ...}` or HTTP 400
  `{"error": ...}`.
- [x] `python3 -m textkit.web` starts the server (add the
  `if __name__ == "__main__":` entry point reading `TEXTKIT_PORT`,
  default 3000, bind 0.0.0.0). Log one line to stdout when ready.
- [x] Unit tests: `transform`-level tests stay green; add a handler test
  for the 400 path if it can be done without sockets, otherwise skip.
  (Request handling was factored into the pure `handle_transform(body)`,
  so the 400 paths and the page markup are covered without sockets.)
- [x] Run `python3 -m unittest discover -s tests -v` — green.

## Task 3: changelog

- [ ] Update `CHANGELOG.md` per repository conventions (changelog skill).
