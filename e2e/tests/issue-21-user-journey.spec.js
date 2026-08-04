// Full walkthrough of the spec's "Main user scenario" for snake_case, as one
// continuous journey — kept in a single test so the recorded video shows the
// feature end to end.
//
// E2E_DEMO_PACE_MS (default 0) inserts pauses and visible typing so the
// recorded video is watchable; the assertions are identical either way.
// Spec: docs/superpowers/specs/issue-21-design.md
const { test, expect } = require("@playwright/test");
const { PLACEHOLDER } = require("./constants");

const PACE_MS = Number(process.env.E2E_DEMO_PACE_MS || 0);

async function pace(page) {
  if (PACE_MS > 0) await page.waitForTimeout(PACE_MS);
}

async function enterText(page, text) {
  await page.fill("#text", "");
  if (PACE_MS > 0) {
    await page.locator("#text").pressSequentially(text, { delay: 90 });
  } else {
    await page.fill("#text", text);
  }
}

test.describe("issue-21 — snake_case user journey", () => {
  test("open, type Café au lait, apply snake_case, contrast with slugify, clear", async ({
    page,
  }) => {
    test.setTimeout(PACE_MS > 0 ? 120_000 : 15_000);

    // 1. Open the playground.
    await page.goto("/");
    await expect(page).toHaveTitle("textkit playground");
    await expect(page.locator("#result")).toHaveText(PLACEHOLDER);
    await expect(page.locator('#op option[value="snake_case"]')).toHaveText(
      "snake_case"
    );
    await expect(page.locator("footer#footer")).toHaveText(
      "textkit playground · 7 operations"
    );
    await pace(page);

    // 2-4. Type the accented sample, pick snake_case, press Apply.
    await enterText(page, "Café au lait");
    await expect(page.locator("#charcount")).toHaveText("12 characters");
    await pace(page);
    await page.selectOption("#op", "snake_case");
    await pace(page);
    let responded = page.waitForResponse("**/api/transform");
    await page.click("#apply");
    await responded;

    // 5. The result is the snake_case identifier.
    await expect(page.locator("#result")).toHaveText("cafe_au_lait");
    await pace(page);

    // Contrast with slugify on the same input: only the separator differs.
    await page.selectOption("#op", "slugify");
    await pace(page);
    responded = page.waitForResponse("**/api/transform");
    await page.click("#apply");
    await responded;
    await expect(page.locator("#result")).toHaveText("cafe-au-lait");
    await pace(page);

    // Back to snake_case with a second phrase.
    await enterText(page, "Ada Lovelace was a mathematician");
    await page.selectOption("#op", "snake_case");
    await pace(page);
    responded = page.waitForResponse("**/api/transform");
    await page.click("#apply");
    await responded;
    await expect(page.locator("#result")).toHaveText(
      "ada_lovelace_was_a_mathematician"
    );
    await pace(page);

    // 6. Clear empties the text, restores the placeholder and keeps the op.
    await page.click("#clear");
    await expect(page.locator("#text")).toHaveValue("");
    await expect(page.locator("#charcount")).toHaveText("0 characters");
    await expect(page.locator("#result")).toHaveText(PLACEHOLDER);
    await expect(page.locator("#op")).toHaveValue("snake_case");
    await pace(page);
  });
});
