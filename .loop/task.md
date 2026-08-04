# Issue #19: feat: JSON transform API

Labels: loop:ready

Expose the textkit transforms over a JSON HTTP API so that other services (the frontend repo) can consume them.

Requirements:
- `GET /api/transforms` -> `{"transforms": ["slugify", ...]}` — names of all single-argument text transforms available in textkit, sorted.
- `POST /api/transform` with JSON body `{"fn": "<name>", "text": "<input>"}` -> `{"result": "<output>"}`.
- Errors: unknown `fn` or malformed body -> HTTP 400 with `{"error": "<message>"}`. Content-Type `application/json` everywhere.
- These endpoints live in the existing `textkit.web` server (same port). Response shapes are a public contract consumed by another repository — keep them exactly as specified.
- Unit tests for both endpoints including the error cases.
