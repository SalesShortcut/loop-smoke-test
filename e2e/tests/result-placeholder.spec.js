// E2E scenarios for the playground result placeholder.
// Spec: docs/superpowers/specs/2026-08-03-result-placeholder-design.md
const { test, expect } = require("@playwright/test");

const PLACEHOLDER = "Type something and press Apply Beza";

test.describe("result placeholder — main user scenario", () => {
  test("page opens with the placeholder, Apply replaces it, Clear restores it", async ({
    page,
  }) => {
    // 1. Open `/` — the result area shows the placeholder.
    await page.goto("/");
    await expect(page.locator("#result")).toHaveText(PLACEHOLDER);

    // 2. Type Ada Lovelace, pick slugify, press Apply — result appears.
    await page.fill("#text", "Ada Lovelace");
    await page.selectOption("#op", "slugify");
    await page.click("#apply");
    await expect(page.locator("#result")).toHaveText("ada-lovelace");

    // 3. Clear — textarea empties, counter resets, placeholder returns.
    await page.click("#clear");
    await expect(page.locator("#text")).toHaveValue("");
    await expect(page.locator("#charcount")).toHaveText("0 characters");
    await expect(page.locator("#result")).toHaveText(PLACEHOLDER);
  });
});

test.describe("result placeholder — critical paths", () => {
  test("the served markup contains the exact placeholder string", async ({
    request,
  }) => {
    const response = await request.get("/");
    expect(response.status()).toBe(200);
    const body = await response.text();
    expect(body).toContain(
      '<output id="result">Type something and press Apply Beza</output>'
    );
  });

  test("clear on a pristine page keeps the placeholder", async ({ page }) => {
    await page.goto("/");
    await page.click("#clear");
    await expect(page.locator("#result")).toHaveText(PLACEHOLDER);
  });

  test("clear restores the placeholder even after an error result", async ({
    page,
  }) => {
    await page.goto("/");
    // Force an unknown op into the DOM to land an error in #result.
    await page.evaluate(() => {
      const option = document.querySelector("#op option");
      option.value = "nope";
      option.textContent = "nope";
    });
    await page.fill("#text", "anything");
    await page.selectOption("#op", "nope");
    await page.click("#apply");
    await expect(page.locator("#result")).toContainText("nope");

    await page.click("#clear");
    await expect(page.locator("#result")).toHaveText(PLACEHOLDER);
  });

  test("the playground still works after the placeholder is restored", async ({
    page,
  }) => {
    await page.goto("/");
    await page.fill("#text", "Ada Lovelace");
    await page.selectOption("#op", "slugify");
    await page.click("#apply");
    await expect(page.locator("#result")).toHaveText("ada-lovelace");

    await page.click("#clear");
    await expect(page.locator("#result")).toHaveText(PLACEHOLDER);

    await page.fill("#text", "Grace Hopper");
    await page.selectOption("#op", "initials");
    await page.click("#apply");
    await expect(page.locator("#result")).toHaveText("G.H.");
  });
});
