// Records a human-paced walkthrough of the footer main scenario
// (docs/superpowers/specs/2026-08-03-footer-design.md) for .loop/e2e/main.mp4.
// Not a test — run with: node record-main.js
const { chromium } = require("@playwright/test");

const BASE = process.env.E2E_BASE_URL || "http://localhost:3000";

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 },
    recordVideo: { dir: "main-video", size: { width: 1280, height: 720 } },
  });
  const page = await context.newPage();

  // 1. Open / — the bottom of the page shows the footer.
  await page.goto(BASE + "/");
  await page.locator("footer#footer").scrollIntoViewIfNeeded();
  await page.waitForTimeout(2500);

  // 2. The footer is static: typing, Apply and Clear do not change it.
  await page.locator("#text").pressSequentially("Ada Lovelace", { delay: 120 });
  await page.waitForTimeout(1500);
  await page.selectOption("#op", "slugify");
  await page.waitForTimeout(1000);
  await page.click("#apply");
  await page.waitForTimeout(2500);
  await page.click("#clear");
  await page.waitForTimeout(2500);

  await context.close(); // flushes the video
  await browser.close();
})();
