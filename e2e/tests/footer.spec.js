// E2E scenarios for the playground footer.
// Spec: docs/superpowers/specs/2026-08-03-footer-design.md
const { test, expect } = require("@playwright/test");
const { PLACEHOLDER } = require("./constants");

// Locked decision: exact text with a middle-dot separator, N = 5 operations.
const FOOTER_TEXT = "textkit playground · 5 operations";

test.describe("footer main scenario", () => {
  test("the bottom of the page shows the operation count", async ({ page }) => {
    await page.goto("/");
    const footer = page.locator("footer#footer");
    await expect(footer).toBeVisible();
    await expect(footer).toHaveText(FOOTER_TEXT);
  });

  test("footer sits after the result paragraph", async ({ page }) => {
    await page.goto("/");
    // The result's <p> wrapper must precede the footer in document order.
    const follows = await page.evaluate(() => {
      const result = document.querySelector("#result").closest("p");
      const footer = document.querySelector("footer#footer");
      return Boolean(
        result.compareDocumentPosition(footer) &
          Node.DOCUMENT_POSITION_FOLLOWING
      );
    });
    expect(follows).toBe(true);
  });
});

test.describe("footer critical paths", () => {
  test("typing, Apply and Clear leave the footer unchanged", async ({
    page,
  }) => {
    await page.goto("/");
    const footer = page.locator("footer#footer");
    await expect(footer).toHaveText(FOOTER_TEXT);

    await page.fill("#text", "Ada Lovelace");
    await expect(footer).toHaveText(FOOTER_TEXT);

    await page.selectOption("#op", "slugify");
    const responded = page.waitForResponse("**/api/transform");
    await page.click("#apply");
    await responded;
    await expect(page.locator("#result")).toHaveText("ada-lovelace");
    await expect(footer).toHaveText(FOOTER_TEXT);

    await page.click("#clear");
    await expect(page.locator("#result")).toHaveText(PLACEHOLDER);
    await expect(footer).toHaveText(FOOTER_TEXT);
  });

  test("the footer count matches the number of options in the select", async ({
    page,
  }) => {
    await page.goto("/");
    const optionCount = await page.locator("#op option").count();
    await expect(page.locator("footer#footer")).toHaveText(
      `textkit playground · ${optionCount} operations`
    );
  });
});
