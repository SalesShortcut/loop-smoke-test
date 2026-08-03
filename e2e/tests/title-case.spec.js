// E2E scenarios for the playground Title Case button.
// Spec: docs/superpowers/specs/issue-15-design.md
const { test, expect } = require("@playwright/test");
const { PLACEHOLDER } = require("./constants");

test.describe("Title Case button — main user scenario", () => {
  test("typing a sentence and clicking Title Case fills #result", async ({
    page,
  }) => {
    await page.goto("/");
    await page.fill("#text", "ada lovelace and the analytical engine");
    const responded = page.waitForResponse("**/api/transform");
    await page.click("#title-case");
    await responded;
    await expect(page.locator("#result")).toHaveText(
      "Ada Lovelace and the Analytical Engine"
    );
  });
});

test.describe("Title Case button — critical paths", () => {
  test("the button is visible and sits after Clear", async ({ page }) => {
    await page.goto("/");
    const button = page.locator("button#title-case");
    await expect(button).toBeVisible();
    await expect(button).toHaveText("Title Case");
    const follows = await page.evaluate(() => {
      const clear = document.querySelector("button#clear");
      const titleCase = document.querySelector("button#title-case");
      return Boolean(
        clear.compareDocumentPosition(titleCase) &
          Node.DOCUMENT_POSITION_FOLLOWING
      );
    });
    expect(follows).toBe(true);
  });

  test("the button works without touching #op", async ({ page }) => {
    await page.goto("/");
    await page.fill("#text", "a tale of two cities");
    const responded = page.waitForResponse("**/api/transform");
    await page.click("#title-case");
    await responded;
    await expect(page.locator("#result")).toHaveText("A Tale of Two Cities");
    // Locked decision: the new button never mutates the select.
    await expect(page.locator("#op")).toHaveValue("slugify");
  });

  test("a connector word in first position is capitalised", async ({
    page,
  }) => {
    await page.goto("/");
    await page.fill("#text", "the analytical engine");
    const responded = page.waitForResponse("**/api/transform");
    await page.click("#title-case");
    await responded;
    await expect(page.locator("#result")).toHaveText("The Analytical Engine");
  });

  test("Clear still works after a title-case run", async ({ page }) => {
    await page.goto("/");
    await page.fill("#text", "ada lovelace and the analytical engine");
    const responded = page.waitForResponse("**/api/transform");
    await page.click("#title-case");
    await responded;
    await expect(page.locator("#result")).toHaveText(
      "Ada Lovelace and the Analytical Engine"
    );

    await page.click("#clear");
    await expect(page.locator("#text")).toHaveValue("");
    await expect(page.locator("#result")).toHaveText(PLACEHOLDER);
  });
});

test.describe("Title Case — API critical path (request-level)", () => {
  test("POST /api/transform title-cases the text", async ({ request }) => {
    const response = await request.post("/api/transform", {
      data: { op: "title_case", text: "a tale of two cities" },
    });
    expect(response.status()).toBe(200);
    expect(await response.json()).toEqual({ result: "A Tale of Two Cities" });
  });
});
