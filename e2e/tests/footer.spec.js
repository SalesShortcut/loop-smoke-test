// E2E scenarios for the playground footer.
// Spec: docs/superpowers/specs/2026-08-03-footer-design.md
const { test, expect } = require("@playwright/test");
const { PLACEHOLDER } = require("./constants");

const FOOTER_TEXT = "textkit playground · 5 operations";

test.describe("footer main scenario", () => {
  test("bottom of the page shows the operation count", async ({ page }) => {
    await page.goto("/");
    const footer = page.locator("footer#footer");
    await expect(footer).toBeVisible();
    await expect(footer).toHaveText(FOOTER_TEXT);
    // The footer sits below the result paragraph.
    const above = await page
      .locator("#result")
      .evaluate(
        (el, sel) =>
          !!(
            el.compareDocumentPosition(document.querySelector(sel)) &
            Node.DOCUMENT_POSITION_FOLLOWING
          ),
        "footer#footer"
      );
    expect(above).toBe(true);
  });

  test("footer is static: typing, Apply and Clear do not change it", async ({
    page,
  }) => {
    await page.goto("/");
    const footer = page.locator("footer#footer");
    await expect(footer).toHaveText(FOOTER_TEXT);

    // Typing updates the char counter but not the footer.
    await page.fill("#text", "Ada Lovelace");
    await expect(page.locator("#charcount")).toHaveText("12 characters");
    await expect(footer).toHaveText(FOOTER_TEXT);

    // Apply transforms the text but leaves the footer untouched.
    await page.selectOption("#op", "slugify");
    const responded = page.waitForResponse("**/api/transform");
    await page.click("#apply");
    await responded;
    await expect(page.locator("#result")).toHaveText("ada-lovelace");
    await expect(footer).toHaveText(FOOTER_TEXT);

    // Clear resets input and result but leaves the footer untouched.
    await page.click("#clear");
    await expect(page.locator("#result")).toHaveText(PLACEHOLDER);
    await expect(footer).toHaveText(FOOTER_TEXT);
  });
});

test.describe("footer critical paths", () => {
  test("footer is server-rendered, not injected by JavaScript", async ({
    request,
  }) => {
    const response = await request.get("/");
    expect(response.status()).toBe(200);
    const body = await response.text();
    expect(body).toContain(
      '<footer id="footer">textkit playground · 5 operations</footer>'
    );
  });

  test("footer count matches the number of ops in the select", async ({
    page,
  }) => {
    await page.goto("/");
    const optionCount = await page.locator("#op option").count();
    await expect(page.locator("footer#footer")).toHaveText(
      `textkit playground · ${optionCount} operations`
    );
  });
});
