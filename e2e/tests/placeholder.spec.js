// E2E scenarios for the playground textarea placeholder hint.
// Spec: docs/superpowers/specs/2026-08-01-textarea-placeholder-design.md
const { test, expect } = require("@playwright/test");

const HINT = "Type your text…";

test.describe("main user scenario", () => {
  test("empty textarea shows the hint, typing hides it, Clear brings it back", async ({
    page,
  }) => {
    await page.goto("/");

    // 1. Open `/` — the empty textarea shows the hint.
    const textarea = page.locator("textarea#text");
    await expect(textarea).toBeVisible();
    await expect(textarea).toHaveAttribute("placeholder", HINT);
    await expect(textarea).toHaveValue("");
    await expect(page.locator("#text:placeholder-shown")).toHaveCount(1);

    // 2. Type any text — the hint disappears (native browser behaviour).
    await textarea.fill("Ada Lovelace");
    await expect(page.locator("#text:placeholder-shown")).toHaveCount(0);

    // ...and the playground works as before.
    await page.selectOption("#op", "slugify");
    await page.click("#apply");
    await expect(page.locator("#result")).toHaveText("ada-lovelace");

    // 3. Click #clear — the textarea empties and the hint is visible again.
    await page.click("#clear");
    await expect(textarea).toHaveValue("");
    await expect(page.locator("#text:placeholder-shown")).toHaveCount(1);
  });
});

test.describe("critical paths", () => {
  test("hint uses the exact string with the … ellipsis character", async ({
    page,
  }) => {
    await page.goto("/");
    const placeholder = await page
      .locator("textarea#text")
      .getAttribute("placeholder");
    expect(placeholder).toBe(HINT);
    expect(placeholder).not.toContain("...");
  });

  test("placeholder never becomes the submitted value", async ({ page }) => {
    await page.goto("/");
    // Applying an op on the untouched textarea must send "", not the hint.
    await page.selectOption("#op", "shout");
    await page.click("#apply");
    await expect(page.locator("#result")).toHaveText("");
    await expect(page.locator("#text:placeholder-shown")).toHaveCount(1);
  });

  test("rest of the page is unchanged by the placeholder", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle("textkit playground");
    await expect(page.locator("select#op")).toBeVisible();
    await expect(page.locator("button#apply")).toHaveText("Apply");
    await expect(page.locator("button#clear")).toHaveText("Clear");
    await expect(page.locator("output#result")).toBeAttached();
  });
});
