// E2E scenarios for the playground character counter.
// Spec: docs/superpowers/specs/2026-08-03-char-counter-design.md
const { test, expect } = require("@playwright/test");

test.describe("character counter — main user scenario", () => {
  test("counter tracks typing and clear resets it", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("#charcount")).toHaveText("0 characters");

    await page.fill("#text", "Ada");
    await expect(page.locator("#charcount")).toHaveText("3 characters");

    await page.click("#clear");
    await expect(page.locator("#text")).toHaveValue("");
    await expect(page.locator("#charcount")).toHaveText("0 characters");
  });
});

test.describe("character counter — critical paths", () => {
  test("counter sits directly below the textarea", async ({ page }) => {
    await page.goto("/");
    const textareaBox = await page.locator("#text").boundingBox();
    const counterBox = await page.locator("#charcount").boundingBox();
    expect(counterBox.y).toBeGreaterThan(textareaBox.y + textareaBox.height);
  });

  test("counter follows every edit, including deletions", async ({ page }) => {
    await page.goto("/");
    await page.locator("#text").pressSequentially("Ada Lovelace");
    await expect(page.locator("#charcount")).toHaveText("12 characters");

    await page.locator("#text").press("Backspace");
    await expect(page.locator("#charcount")).toHaveText("11 characters");

    await page.fill("#text", "");
    await expect(page.locator("#charcount")).toHaveText("0 characters");
  });

  test("applying an operation does not change the counter", async ({
    page,
  }) => {
    await page.goto("/");
    await page.fill("#text", "Ada");
    await page.selectOption("#op", "shout");
    await page.click("#apply");
    await expect(page.locator("#result")).toHaveText("ADA");
    await expect(page.locator("#charcount")).toHaveText("3 characters");
  });
});
