# JSON transform API — design

Issue: #19 (`.loop/task.md`)
Date: 2026-08-03
Status: approved

## What we are building

Two JSON endpoints on the existing `textkit.web` server (same process, same
port) so another repository — the frontend — can discover and call the textkit
transforms over HTTP:

- `GET /api/transforms` → `200 {"transforms": ["initials", ...]}` — the names
  of the available single-argument text transforms, sorted.
- `POST /api/transform` with `{"fn": "<name>", "text": "<input>"}` →
  `200 {"result": "<output>"}`.
- Unknown `fn` or a malformed body → `400 {"error": "<message>"}`.
- Every API response carries `Content-Type: application/json; charset=utf-8`.

Plus unit tests for both endpoints, including the error paths.

## Why

`textkit.web` already exposes the transforms, but only as an implementation
detail of its own HTML playground: the discovery list exists solely as
`<option>` tags inside the rendered page, and the POST body field is named
`op`, which the issue does not use. A second consumer cannot scrape HTML for
the list of transforms, so it needs a machine-readable index endpoint and a
POST contract stated in the issue's own terms. The endpoints are a published
contract for another repo, so the shapes above are fixed and must not drift.

## Starting point (what already exists)

`textkit/web.py` today:

- `OPERATIONS: dict[str, Callable[[str], str]]` — six entries: `slugify`,
  `shout`, `initials`, `reverse_words`, `truncate` (a lambda binding
  `core.truncate(text, TRUNCATE_WIDTH)` so it takes one argument),
  `title_case`. Insertion order drives the `<select>` option order, which e2e
  pins — **do not reorder it**.
- `transform(op, text)` — dispatcher, raises `ValueError` on an unknown name.
- `handle_transform(body: bytes) -> tuple[int, dict]` — parses a POST body,
  returns `(200, {"result": ...})` or `(400, {"error": ...})`. It reads the
  field **`op`**, not `fn`.
- `PlaygroundHandler.do_GET` serves the page at `/` and JSON-404s everything
  else; `do_POST` routes only `/api/transform` (with a 413 guard above
  `MAX_BODY_BYTES`) and JSON-404s everything else.
- The playground page script POSTs `{op, text}` to `/api/transform`.

So `POST /api/transform` already exists at the requested path and already
returns the requested response shapes; only the **request field name**
differs. `GET /api/transforms` does not exist at all.

## Locked decisions

### 1. `fn` is canonical, `op` stays as a legacy alias

The issue's request body is `{"fn": ..., "text": ...}`. The same path already
takes `{"op": ..., "text": ...}` and is called that way by the playground page
script, by `tests/test_web.py` and by two request-level Playwright tests.

Decision: `handle_transform` accepts **both** field names.

- If the key `fn` is present, its value is used — regardless of `op`.
- Otherwise the value of `op` is used, if present.
- Otherwise the request is missing a transform name → 400.
- The selected value must be a `str`; anything else (including `None`,
  numbers, lists) → 400.

Shape of the lookup (order matters — `fn` wins even when it is present and
invalid, so a caller who sends `fn` never gets silently served by a stale
`op`):

```python
name = payload["fn"] if "fn" in payload else payload.get("op")
if not isinstance(name, str):
    return 400, {"error": '"fn" must be a string'}
```

Rationale: the issue's contract is satisfied exactly, and nothing that works
today stops working. Removing `op` was rejected — it would break the served
page and three existing tests for no gain the issue asks for, and the issue
constrains *response* shapes, not the repo's internal callers.

Consequence, accepted: two field names are accepted forever on this endpoint.
The alias is documented in the README table and in the `handle_transform`
docstring, and it keeps working precisely because the existing `op`-based
tests are left in place as its regression coverage.

### 2. The playground page script switches to `fn`

`render_page`'s `applyOp` helper sends `{fn: op, text: ...}`. The rest of the
page — ids, labels, char counter, Clear, placeholder, footer — is untouched.

Rationale: one canonical field is actually exercised in-repo. The legacy alias
keeps its coverage from the request-level tests that still send `op`.

### 3. `GET /api/transforms` returns `sorted(OPERATIONS)`

New helper in `textkit/web.py`:

```python
def list_transforms() -> dict:
    """Return the JSON payload for GET /api/transforms. ..."""
    return {"transforms": sorted(OPERATIONS)}
```

The payload is therefore exactly:

```json
{"transforms": ["initials", "reverse_words", "shout", "slugify", "title_case", "truncate"]}
```

- Sorted alphabetically (the issue says "sorted"), **not** in `OPERATIONS`
  insertion order — the page's `<select>` order is a separate concern and
  stays as it is.
- The list is derived from `OPERATIONS`, never hard-coded, so the endpoint and
  the set of names `POST /api/transform` accepts cannot drift apart.
- Exactly one key, `transforms`. No count, no descriptions, no metadata.

**Interpretation note (the one real ambiguity in the issue).** The issue says
"names of all single-argument text transforms available in textkit". Read
against the library, that phrase would exclude `truncate` (`core.truncate`
takes `text` *and* `width`) and it already excludes `word_count` (one argument,
but returns an `int`, so not a text transform). We nevertheless list
`truncate`, because at the API boundary it *is* a single-argument text
transform: `OPERATIONS["truncate"]` binds `width=TRUNCATE_WIDTH` (20) and takes
`str -> str` like every other entry. The decisive argument is consistency: the
frontend will feed the names from `GET /api/transforms` straight into
`POST /api/transform`, so the advertised list must equal the accepted set.
Omitting `truncate` would leave a name that works but is undiscoverable.

If the issue author meant the strict library reading, the fix is one line
(`sorted(OPERATIONS)` → an explicit exclusion) plus the assertions in
criteria 1 and 5 below; flag it on review rather than after the frontend has
shipped against six names.

### 4. Routing and status codes

- `do_GET` matches the path with the query string stripped
  (`self.path.split("?", 1)[0]`, as today):
  - `/` → the HTML page, as today.
  - `/api/transforms` → `200` + `list_transforms()` as JSON.
  - anything else → `404 {"error": "not found"}` as today.
- `do_POST` is unchanged apart from `handle_transform`'s field handling: only
  `/api/transform` routes; the `MAX_BODY_BYTES` → `413 {"error": "body too
  large"}` guard stays exactly as it is.
- Method/path mismatches keep today's behaviour: `GET /api/transform`,
  `POST /api/transforms`, and `/api/transforms/` (trailing slash) all return
  `404 {"error": "not found"}` in JSON. No `405`, no redirects — the issue
  asks for 400 on bad *bodies*, not for method negotiation.
- No trailing-slash tolerance, no path normalisation.

### 5. Error messages

The contract fixes the error *shape* (`{"error": "<string>"}`), not the
wording. Existing messages are kept verbatim so no current assertion moves:

| situation | status | body |
| --- | --- | --- |
| body is not UTF-8 / not JSON | 400 | `{"error": "body must be valid JSON"}` |
| body is JSON but not an object | 400 | `{"error": "body must be a JSON object"}` |
| `fn`/`op` missing or not a string | 400 | `{"error": "\"fn\" must be a string"}` |
| `text` missing or not a string | 400 | `{"error": "\"text\" must be a string"}` |
| unknown transform name | 400 | `{"error": "unknown op: 'nope'"}` |
| body over `MAX_BODY_BYTES` | 413 | `{"error": "body too large"}` |
| unrouted path | 404 | `{"error": "not found"}` |

The unknown-name message keeps the word "op" because it comes from
`transform()`, whose parameter is `op` and whose doctest pins the text.
Guaranteed and asserted: the message always contains the offending name.

### 6. House rules

- Standard library only; no new imports beyond what `web.py` already has.
- `list_transforms` gets a docstring with an `Example:` section (CLAUDE.md).
- New helpers live in `textkit/web.py` and are **not** re-exported from
  `textkit/__init__.py`: that module exports the pure-library `core`
  functions only, and every existing web helper (`transform`,
  `handle_transform`, `render_page`, `serve`, `port_from_env`) follows that
  precedent. Re-exporting would pull `http.server` into every `import textkit`.
- One entry per new public function appended to `CHANGELOG.md` per the
  `changelog` skill, in the feature commit.
- Commit message prefixed `[textkit] `. No `__pycache__/` or `*.pyc`.

## Acceptance criteria

1. `GET /api/transforms` returns `200`,
   `Content-Type: application/json; charset=utf-8`, and the body
   `{"transforms": ["initials", "reverse_words", "shout", "slugify", "title_case", "truncate"]}`
   — one key, list sorted ascending.
2. `list_transforms()["transforms"] == sorted(OPERATIONS)` — the endpoint is
   derived, not hard-coded.
3. Every name returned by `GET /api/transforms` is accepted by
   `POST /api/transform` with a `200` response (asserted by iterating the
   list), and `word_count` is not among them.
4. `GET /api/transforms?x=1` behaves identically to `GET /api/transforms`.
5. `POST /api/transform` with `{"fn": "slugify", "text": "Ada Lovelace"}`
   returns `200 {"result": "ada-lovelace"}` and
   `Content-Type: application/json; charset=utf-8`.
6. `POST /api/transform` with `{"op": "slugify", "text": "Ada Lovelace"}`
   still returns `200 {"result": "ada-lovelace"}` (legacy alias).
7. When both are present, `fn` wins: `{"fn": "shout", "op": "slugify",
   "text": "hi"}` → `{"result": "HI"}`.
8. `POST /api/transform` with `{"fn": "nope", "text": "x"}` returns `400`,
   a body with an `error` string containing `nope`, and **no** `result` key.
9. Malformed bodies all return `400` with an `error` string and no `result`:
   `{not json`, empty body, `[1, 2, 3]`, `{"text": "hi"}` (no name),
   `{"fn": 1, "text": "x"}`, `{"fn": "shout"}` (no text),
   `{"fn": "shout", "text": 1}`.
10. `GET /api/transform`, `POST /api/transforms` and `GET /api/transforms/`
    return `404 {"error": "not found"}` with the JSON content type.
11. The playground page still works end to end: typing text and clicking
    Apply/Title Case fills `#result`; the page script posts `fn`.
12. `python3 -m unittest discover -s tests -v` is green — the 75 existing
    tests still pass unmodified, plus the new ones.
13. The Playwright suite is green, including a request-level spec covering
    both endpoints.
14. `CHANGELOG.md` gains its entries in the feature commit, in the skill's
    format.

## Main consumer scenario

1. The frontend service calls `GET /api/transforms` once and renders a picker
   from `data.transforms`.
2. The user picks `title_case` and types `a tale of two cities`.
3. The frontend calls
   `POST /api/transform` with `{"fn": "title_case", "text": "a tale of two cities"}`.
4. It receives `200 {"result": "A Tale of Two Cities"}` and displays it.
5. A typo (`{"fn": "titlecase"}`) yields `400 {"error": "unknown op: 'titlecase'"}`,
   which the frontend shows as an error without special-casing status codes:
   `error` is present whenever the request was not a `200`.

## Out of scope

- CORS headers (`Access-Control-Allow-Origin`), preflight `OPTIONS` handling,
  and any other cross-origin support. The issue does not ask for it; if the
  frontend is served from a different origin it will need a follow-up issue.
  Flagged deliberately — this is the most likely immediate follow-up.
- Authentication, rate limiting, request logging, API versioning
  (`/api/v1/...`).
- Multi-argument transforms: `truncate`'s width stays fixed at
  `TRUNCATE_WIDTH` (20) and is not configurable per request. `word_count`
  stays unexposed (it returns an `int`, not text).
- Batch requests, streaming, `GET /api/transform?fn=...` as an alternative.
- Removing the `op` alias, and any change to `transform()`'s signature or its
  error wording.
- Reordering `OPERATIONS` or changing the `<select>`, footer count, char
  counter, Clear behaviour, placeholder or styling of the playground page.
- 405 responses / `Allow` headers for method mismatches.
