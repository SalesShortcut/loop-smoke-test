// End-to-end verification of the JSON transform API from a consumer's
// point of view, following the spec's "Main consumer scenario" section.
// Spec: docs/superpowers/specs/issue-19-design.md
const { test, expect } = require("@playwright/test");

test.describe("issue-19 — main consumer scenario (request-level)", () => {
  test("discover transforms, apply title_case, get a friendly error on a typo", async ({
    request,
  }) => {
    // 1. The frontend calls GET /api/transforms once and renders a picker.
    const listResponse = await request.get("/api/transforms");
    expect(listResponse.status()).toBe(200);
    expect(listResponse.headers()["content-type"]).toBe(
      "application/json; charset=utf-8"
    );
    const { transforms } = await listResponse.json();
    expect(transforms).toEqual([
      "initials",
      "reverse_words",
      "shout",
      "slugify",
      "title_case",
      "truncate",
    ]);

    // 2-4. The user picks title_case; the frontend POSTs {fn, text}.
    expect(transforms).toContain("title_case");
    const okResponse = await request.post("/api/transform", {
      data: { fn: "title_case", text: "a tale of two cities" },
    });
    expect(okResponse.status()).toBe(200);
    expect(okResponse.headers()["content-type"]).toBe(
      "application/json; charset=utf-8"
    );
    expect(await okResponse.json()).toEqual({ result: "A Tale of Two Cities" });

    // 5. A typo yields a 400 whose body carries `error` — no status-code
    // special-casing needed by the frontend.
    const typoResponse = await request.post("/api/transform", {
      data: { fn: "titlecase", text: "a tale of two cities" },
    });
    expect(typoResponse.status()).toBe(400);
    const typoBody = await typoResponse.json();
    expect(typeof typoBody.error).toBe("string");
    expect(typoBody.error).toContain("titlecase");
    expect(typoBody).not.toHaveProperty("result");
  });

  test("the advertised list equals the accepted set", async ({ request }) => {
    const { transforms } = await (await request.get("/api/transforms")).json();
    for (const fn of transforms) {
      const response = await request.post("/api/transform", {
        data: { fn, text: "Ada Lovelace was a mathematician" },
      });
      expect(response.status(), `fn=${fn}`).toBe(200);
      expect(typeof (await response.json()).result, `fn=${fn}`).toBe("string");
    }
    expect(transforms).not.toContain("word_count");
  });

  test("fn wins over op, and op alone still works", async ({ request }) => {
    const both = await request.post("/api/transform", {
      data: { fn: "shout", op: "slugify", text: "hi" },
    });
    expect(await both.json()).toEqual({ result: "HI" });

    const legacy = await request.post("/api/transform", {
      data: { op: "slugify", text: "Ada Lovelace" },
    });
    expect(legacy.status()).toBe(200);
    expect(await legacy.json()).toEqual({ result: "ada-lovelace" });
  });

  test("method/path mismatches are JSON 404s", async ({ request }) => {
    for (const call of [
      () => request.get("/api/transform"),
      () => request.post("/api/transforms", { data: {} }),
      () => request.get("/api/transforms/"),
    ]) {
      const response = await call();
      expect(response.status()).toBe(404);
      expect(response.headers()["content-type"]).toBe(
        "application/json; charset=utf-8"
      );
      expect(await response.json()).toEqual({ error: "not found" });
    }
  });
});

test.describe("issue-19 — the playground still works and posts fn (criterion 11)", () => {
  test("typing text and clicking Title Case fills #result via the fn field", async ({
    page,
  }) => {
    await page.goto("/");
    await page.fill("#text", "a tale of two cities");

    const requestPromise = page.waitForRequest("**/api/transform");
    const responded = page.waitForResponse("**/api/transform");
    await page.click("#title-case");
    const sent = await requestPromise;
    await responded;

    // The page script posts the canonical field, not the legacy alias.
    const body = sent.postDataJSON();
    expect(body).toEqual({ fn: "title_case", text: "a tale of two cities" });

    await expect(page.locator("#result")).toHaveText("A Tale of Two Cities");
  });

  test("Apply uses the selected operation through fn", async ({ page }) => {
    await page.goto("/");
    await page.fill("#text", "Ada Lovelace");
    await page.selectOption("#op", "slugify");

    const requestPromise = page.waitForRequest("**/api/transform");
    const responded = page.waitForResponse("**/api/transform");
    await page.click("#apply");
    const sent = await requestPromise;
    await responded;

    expect(sent.postDataJSON()).toEqual({ fn: "slugify", text: "Ada Lovelace" });
    await expect(page.locator("#result")).toHaveText("ada-lovelace");
  });
});
