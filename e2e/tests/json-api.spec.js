// E2E scenarios for the JSON transform API (request-level only).
// Spec: docs/superpowers/specs/issue-19-design.md
const { test, expect } = require("@playwright/test");

const NAMES = [
  "initials",
  "reverse_words",
  "shout",
  "slugify",
  "title_case",
  "truncate",
];

test.describe("JSON transform API — main consumer scenario", () => {
  test("GET /api/transforms lists the sorted transform names", async ({
    request,
  }) => {
    const response = await request.get("/api/transforms");
    expect(response.status()).toBe(200);
    expect(response.headers()["content-type"]).toContain("application/json");
    expect(await response.json()).toEqual({ transforms: NAMES });
  });

  test("every listed name is accepted by POST /api/transform", async ({
    request,
  }) => {
    const listed = await (await request.get("/api/transforms")).json();
    for (const fn of listed.transforms) {
      const response = await request.post("/api/transform", {
        data: { fn, text: "Ada Lovelace was a mathematician" },
      });
      expect(response.status(), `fn=${fn}`).toBe(200);
      expect(typeof (await response.json()).result, `fn=${fn}`).toBe("string");
    }
  });

  test("POST /api/transform title-cases the text via fn", async ({
    request,
  }) => {
    const response = await request.post("/api/transform", {
      data: { fn: "title_case", text: "a tale of two cities" },
    });
    expect(response.status()).toBe(200);
    expect(await response.json()).toEqual({ result: "A Tale of Two Cities" });
  });
});

test.describe("JSON transform API — error paths", () => {
  test("an unknown fn is a 400 with a string error", async ({ request }) => {
    const response = await request.post("/api/transform", {
      data: { fn: "nope", text: "x" },
    });
    expect(response.status()).toBe(400);
    const body = await response.json();
    expect(typeof body.error).toBe("string");
    expect(body.error).toContain("nope");
  });

  test("a malformed body is a 400 with a string error", async ({ request }) => {
    const response = await request.post("/api/transform", {
      headers: { "Content-Type": "application/json" },
      data: "{not json",
    });
    expect(response.status()).toBe(400);
    expect(typeof (await response.json()).error).toBe("string");
  });

  test("GET /api/transforms/ is a 404", async ({ request }) => {
    const response = await request.get("/api/transforms/");
    expect(response.status()).toBe(404);
    expect(await response.json()).toEqual({ error: "not found" });
  });
});
