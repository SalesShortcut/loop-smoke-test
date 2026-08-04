// E2E scenarios for the playground snake_case operation.
// Spec: docs/superpowers/specs/issue-21-design.md
const { test, expect } = require("@playwright/test");
const { PLACEHOLDER } = require("./constants");

async function applyOp(page, op, text) {
  await page.fill("#text", text);
  await page.selectOption("#op", op);
  // Wait on the transform request itself, as the other specs do.
  const responded = page.waitForResponse("**/api/transform");
  await page.click("#apply");
  await responded;
}

test.describe("snake_case — main user scenario", () => {
  test("selecting snake_case and pressing Apply fills #result", async ({
    page,
  }) => {
    await page.goto("/");
    await applyOp(page, "snake_case", "Café au lait");
    await expect(page.locator("#result")).toHaveText("cafe_au_lait");
  });
});

test.describe("snake_case — critical paths", () => {
  test("the operation is offered as the last option in #op", async ({
    page,
  }) => {
    await page.goto("/");
    const option = page.locator('#op option[value="snake_case"]');
    await expect(option).toHaveCount(1);
    await expect(option).toHaveText("snake_case");
    const values = await page
      .locator("#op option")
      .evaluateAll((options) => options.map((option) => option.value));
    expect(values[values.length - 1]).toBe("snake_case");
  });

  test("no snake_case button was added to the action row", async ({ page }) => {
    // Locked decision: the operation lives in the select only.
    await page.goto("/");
    await expect(page.locator("p:has(#apply) button")).toHaveText([
      "Apply",
      "Clear",
      "Title Case",
    ]);
  });

  test("slugify and snake_case differ only in the separator", async ({
    page,
  }) => {
    await page.goto("/");
    await applyOp(page, "slugify", "Café au lait");
    await expect(page.locator("#result")).toHaveText("cafe-au-lait");
    await applyOp(page, "snake_case", "Café au lait");
    await expect(page.locator("#result")).toHaveText("cafe_au_lait");
  });

  test("Clear still works after a snake_case run", async ({ page }) => {
    await page.goto("/");
    await applyOp(page, "snake_case", "Ada Lovelace");
    await expect(page.locator("#result")).toHaveText("ada_lovelace");

    await page.click("#clear");
    await expect(page.locator("#text")).toHaveValue("");
    await expect(page.locator("#result")).toHaveText(PLACEHOLDER);
    await expect(page.locator("#op")).toHaveValue("snake_case");
  });
});

test.describe("snake_case — API critical paths (request-level)", () => {
  test("POST /api/transform with fn returns the snake_case result", async ({
    request,
  }) => {
    const response = await request.post("/api/transform", {
      data: { fn: "snake_case", text: "Ada Lovelace" },
    });
    expect(response.status()).toBe(200);
    expect(await response.json()).toEqual({ result: "ada_lovelace" });
  });

  test("the legacy op field still works for the new name", async ({
    request,
  }) => {
    const response = await request.post("/api/transform", {
      data: { op: "snake_case", text: "Ada Lovelace" },
    });
    expect(response.status()).toBe(200);
    expect(await response.json()).toEqual({ result: "ada_lovelace" });
  });

  test("GET /api/transforms advertises snake_case", async ({ request }) => {
    const { transforms } = await (await request.get("/api/transforms")).json();
    expect(transforms).toContain("snake_case");
  });
});
