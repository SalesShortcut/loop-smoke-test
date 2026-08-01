// Playwright config for the textkit web playground e2e suite.
// Spec: docs/superpowers/specs/2026-08-01-web-playground-design.md
const { defineConfig, devices } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./tests",
  outputDir: "./test-results",
  timeout: 15_000,
  fullyParallel: false,
  reporter: [["list"], ["json", { outputFile: "test-results/report.json" }]],
  use: {
    baseURL: process.env.E2E_BASE_URL || "http://localhost:3000",
    headless: true,
    viewport: { width: 1280, height: 720 },
    video: { mode: "on", size: { width: 1280, height: 720 } },
    ...devices["Desktop Chrome"],
  },
});
