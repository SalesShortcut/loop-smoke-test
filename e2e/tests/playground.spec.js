// E2E scenarios for the textkit web playground.
// Specs: docs/superpowers/specs/2026-08-01-web-playground-design.md
//        docs/superpowers/specs/2026-08-01-clear-button-design.md
const { test, expect } = require("@playwright/test");
const { PLACEHOLDER } = require("./constants");

const SAMPLE = "Ada Lovelace was a mathematician";

// Expected values mirror textkit.core; truncate uses the playground width 20.
const OPERATIONS = {
  slugify: "ada-lovelace-was-a-mathematician",
  shout: "ADA LOVELACE WAS A MATHEMATICIAN",
  initials: "A.L.W.A.M.",
  reverse_words: "mathematician a was Lovelace Ada",
  truncate: "Ada Lovelace was...",
};

async function applyOp(page, op, text) {
  await page.fill("#text", text);
  await page.selectOption("#op", op);
  // Wait on the transform request itself: a text-based wait would hang if a
  // result ever legitimately equalled the placeholder text.
  const responded = page.waitForResponse("**/api/transform");
  await page.click("#apply");
  await responded;
}

test.describe("main user scenario", () => {
  test("page shows the playground elements", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle("textkit playground");
    await expect(page.locator("textarea#text")).toBeVisible();
    await expect(page.locator("select#op")).toBeVisible();
    await expect(page.locator("button#apply")).toBeVisible();
    await expect(page.locator("button#clear")).toBeVisible();
    await expect(page.locator("output#result")).toBeAttached();
    await expect(page.locator("#result")).toHaveText(PLACEHOLDER);
    await expect(page.locator("#op option")).toHaveText(
      Object.keys(OPERATIONS)
    );
  });

  test("slugify Ada Lovelace shows ada-lovelace in #result", async ({
    page,
  }) => {
    await page.goto("/");
    await applyOp(page, "slugify", "Ada Lovelace");
    await expect(page.locator("#result")).toHaveText("ada-lovelace");
  });

  test("clear empties #text, restores the placeholder, keeps the op", async ({
    page,
  }) => {
    await page.goto("/");
    await applyOp(page, "slugify", "Ada Lovelace");
    await expect(page.locator("#result")).toHaveText("ada-lovelace");
    await page.click("#clear");
    await expect(page.locator("#text")).toHaveValue("");
    await expect(page.locator("#result")).toHaveText(PLACEHOLDER);
    await expect(page.locator("#op")).toHaveValue("slugify");
  });
});

test.describe("critical paths", () => {
  for (const [op, expected] of Object.entries(OPERATIONS)) {
    test(`operation ${op} matches textkit.core`, async ({ page }) => {
      await page.goto("/");
      await applyOp(page, op, SAMPLE);
      await expect(page.locator("#result")).toHaveText(expected);
    });
  }

  test("unknown op surfaces the error in #result and the server survives", async ({
    page,
  }) => {
    await page.goto("/");
    // A real select only offers valid ops; force an unknown value into the
    // DOM to exercise the UI error path the spec calls out.
    await page.evaluate(() => {
      const option = document.querySelector("#op option");
      option.value = "nope";
      option.textContent = "nope";
    });
    await applyOp(page, "nope", "anything");
    await expect(page.locator("#result")).toContainText("nope");
    await expect(page.locator("#result")).not.toHaveText("anything");

    // The server must still answer normal requests afterwards.
    await page.goto("/");
    await applyOp(page, "slugify", "Ada Lovelace");
    await expect(page.locator("#result")).toHaveText("ada-lovelace");
  });
});

test.describe("API critical paths (request-level)", () => {
  test("POST /api/transform returns the transform result", async ({
    request,
  }) => {
    const response = await request.post("/api/transform", {
      data: { op: "slugify", text: "Ada Lovelace" },
    });
    expect(response.status()).toBe(200);
    expect(await response.json()).toEqual({ result: "ada-lovelace" });
  });

  test("unknown op returns HTTP 400 with a JSON error", async ({ request }) => {
    const response = await request.post("/api/transform", {
      data: { op: "nope", text: "x" },
    });
    expect(response.status()).toBe(400);
    const body = await response.json();
    expect(typeof body.error).toBe("string");
  });

  test("malformed body returns HTTP 400 with a JSON error", async ({
    request,
  }) => {
    const response = await request.post("/api/transform", {
      headers: { "Content-Type": "application/json" },
      data: "{not json",
    });
    expect(response.status()).toBe(400);
    const body = await response.json();
    expect(typeof body.error).toBe("string");
  });
});
