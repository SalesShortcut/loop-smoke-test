// E2E scenarios for the playground Clear button.
// Spec: docs/superpowers/specs/2026-08-01-clear-button-design.md
const { test, expect } = require("@playwright/test");
const { PLACEHOLDER } = require("./constants");

test.describe("Clear button — main user scenario", () => {
  test("apply slugify then clear empties both fields and keeps the op", async ({
    page,
  }) => {
    await page.goto("/");
    await page.fill("#text", "Ada Lovelace");
    await page.selectOption("#op", "slugify");
    await page.click("#apply");
    await expect(page.locator("#result")).toHaveText("ada-lovelace");

    await page.click("#clear");
    await expect(page.locator("#text")).toHaveValue("");
    await expect(page.locator("#result")).toHaveText(PLACEHOLDER);
    await expect(page.locator("#op")).toHaveValue("slugify");
  });
});

test.describe("Clear button — critical paths", () => {
  test("clear button is rendered next to apply and labelled Clear", async ({
    page,
  }) => {
    await page.goto("/");
    await expect(page.locator("button#clear")).toBeVisible();
    await expect(page.locator("button#clear")).toHaveText("Clear");
    // The action buttons share the same paragraph as the op selector.
    const buttons = page.locator("p:has(#apply) button");
    await expect(buttons).toHaveText(["Apply", "Clear", "Title Case"]);
  });

  test("clear on a pristine page is a harmless no-op", async ({ page }) => {
    await page.goto("/");
    await page.click("#clear");
    await expect(page.locator("#text")).toHaveValue("");
    await expect(page.locator("#result")).toHaveText(PLACEHOLDER);
  });

  test("clear is client-side only — no HTTP request is made", async ({
    page,
  }) => {
    await page.goto("/");
    await page.fill("#text", "Ada Lovelace");
    await page.selectOption("#op", "shout");
    await page.click("#apply");
    await expect(page.locator("#result")).toHaveText("ADA LOVELACE");

    const requests = [];
    page.on("request", (request) => requests.push(request.url()));
    await page.click("#clear");
    await expect(page.locator("#text")).toHaveValue("");
    await expect(page.locator("#result")).toHaveText(PLACEHOLDER);
    expect(requests).toEqual([]);
  });

  test("form still works after clearing", async ({ page }) => {
    await page.goto("/");
    await page.fill("#text", "Ada Lovelace");
    await page.selectOption("#op", "slugify");
    await page.click("#apply");
    await expect(page.locator("#result")).toHaveText("ada-lovelace");

    await page.click("#clear");
    await page.fill("#text", "Grace Hopper");
    await page.selectOption("#op", "initials");
    await page.click("#apply");
    await expect(page.locator("#result")).toHaveText("G.H.");
  });
});
