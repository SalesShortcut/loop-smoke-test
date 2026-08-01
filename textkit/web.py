"""Web playground for textkit: a single page over the core functions.

Run it with ``python3 -m textkit.web``; the port comes from the
``TEXTKIT_PORT`` environment variable (default 3000).
"""

import html
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from . import core

TRUNCATE_WIDTH = 20

OPERATIONS = {
    "slugify": core.slugify,
    "shout": core.shout,
    "initials": core.initials,
    "reverse_words": core.reverse_words,
    "truncate": lambda text: core.truncate(text, TRUNCATE_WIDTH),
}

DEFAULT_PORT = 3000
MAX_BODY_BYTES = 64 * 1024


def transform(op: str, text: str) -> str:
    """Apply the named textkit operation to text.

    Supported ops are the keys of OPERATIONS; `truncate` uses width
    TRUNCATE_WIDTH. An unknown op raises ValueError.

    Example:
        >>> transform("slugify", "Ada Lovelace")
        'ada-lovelace'
    """
    try:
        func = OPERATIONS[op]
    except KeyError:
        raise ValueError(f"unknown op: {op!r}") from None
    return func(text)


def handle_transform(body: bytes) -> tuple[int, dict]:
    """Turn a POST /api/transform body into an HTTP status and JSON payload.

    A well-formed request yields ``(200, {"result": ...})``; malformed JSON,
    a missing or non-string field, or an unknown op yields
    ``(400, {"error": ...})``.

    Example:
        >>> handle_transform(b'{"op": "shout", "text": "hi"}')
        (200, {'result': 'HI'})
    """
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return 400, {"error": "body must be valid JSON"}
    if not isinstance(payload, dict):
        return 400, {"error": "body must be a JSON object"}

    op = payload.get("op")
    text = payload.get("text")
    if not isinstance(op, str):
        return 400, {"error": '"op" must be a string'}
    if not isinstance(text, str):
        return 400, {"error": '"text" must be a string'}

    try:
        return 200, {"result": transform(op, text)}
    except ValueError as err:
        return 400, {"error": str(err)}


def render_page() -> str:
    """Return the playground HTML page.

    Example:
        >>> "<textarea id=\\"text\\"" in render_page()
        True
    """
    options = "\n".join(
        f'        <option value="{html.escape(op)}">{html.escape(op)}</option>'
        for op in OPERATIONS
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>textkit playground</title>
</head>
<body>
  <h1>textkit playground</h1>
  <p><textarea id="text" rows="4" cols="60"></textarea></p>
  <p>
    <select id="op">
{options}
    </select>
    <button id="apply" type="button">Apply</button>
    <button id="clear" type="button">Clear</button>
  </p>
  <p><output id="result"></output></p>
  <script>
    document.getElementById("apply").addEventListener("click", async () => {{
      const out = document.getElementById("result");
      try {{
        const response = await fetch("/api/transform", {{
          method: "POST",
          headers: {{"Content-Type": "application/json"}},
          body: JSON.stringify({{
            op: document.getElementById("op").value,
            text: document.getElementById("text").value,
          }}),
        }});
        const data = await response.json();
        out.textContent = response.ok ? data.result : data.error;
      }} catch (err) {{
        out.textContent = String(err);
      }}
    }});
    document.getElementById("clear").addEventListener("click", () => {{
      document.getElementById("text").value = "";
      document.getElementById("result").textContent = "";
    }});
  </script>
</body>
</html>
"""


class PlaygroundHandler(BaseHTTPRequestHandler):
    """Serve the playground page and the transform API."""

    server_version = "textkit-playground/0.1"

    def do_GET(self) -> None:  # noqa: N802 - name fixed by BaseHTTPRequestHandler
        if self.path.split("?", 1)[0] != "/":
            self._send_json(404, {"error": "not found"})
            return
        self._send(200, "text/html; charset=utf-8", render_page())

    def do_POST(self) -> None:  # noqa: N802 - name fixed by BaseHTTPRequestHandler
        if self.path.split("?", 1)[0] != "/api/transform":
            self._send_json(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        if length > MAX_BODY_BYTES:
            # The unread body would desync a keep-alive connection.
            self.close_connection = True
            self._send_json(413, {"error": "body too large"})
            return
        body = self.rfile.read(length) if length > 0 else b""
        status, payload = handle_transform(body)
        self._send_json(status, payload)

    def _send_json(self, status: int, payload: dict) -> None:
        self._send(status, "application/json; charset=utf-8", json.dumps(payload))

    def _send(self, status: int, content_type: str, body: str) -> None:
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def serve(port: int = DEFAULT_PORT, host: str = "0.0.0.0") -> None:
    """Serve the playground until interrupted.

    Example:
        >>> serve(3000)  # doctest: +SKIP
        textkit playground listening on http://0.0.0.0:3000
    """
    server = ThreadingHTTPServer((host, port), PlaygroundHandler)
    print(f"textkit playground listening on http://{host}:{port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def port_from_env(value: str | None) -> int:
    """Parse a TEXTKIT_PORT value, exiting with a message when invalid.

    Example:
        >>> port_from_env("8080")
        8080
        >>> port_from_env(None)
        3000
    """
    if not value:
        return DEFAULT_PORT
    try:
        return int(value)
    except ValueError:
        sys.exit(f"TEXTKIT_PORT must be an integer, got {value!r}")


if __name__ == "__main__":
    serve(port_from_env(os.environ.get("TEXTKIT_PORT")))
