import { test, expect } from "@playwright/test";

test.describe("Navigation", () => {
  test("should load homepage", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("h2")).toContainText("Book Your Movie Tickets");
  });

  test("should have working navigation links", async ({ page }) => {
    await page.goto("/");

    await expect(page.locator('a:has-text("Home")')).toBeVisible();
    await expect(page.locator('a:has-text("Movies")')).toBeVisible();
    await expect(page.locator('a:has-text("Theaters")')).toBeVisible();
  });

  test("should display app name in header", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("header")).toContainText("BookMyShow");
  });

  test("should show login and register buttons when not authenticated", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator('a:has-text("Login")')).toBeVisible();
    await expect(page.locator('a:has-text("Register")')).toBeVisible();
  });

  test("should display footer", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("footer")).toBeVisible();
    const currentYear = new Date().getFullYear();
    await expect(page.locator("footer")).toContainText(currentYear.toString());
  });

  test("should navigate between pages", async ({ page }) => {
    await page.goto("/");

    await page.click('a:has-text("Movies")');
    await expect(page).toHaveURL(/.*movies/);

    await page.click('a:has-text("Home")');
    await expect(page).toHaveURL("/");
  });

  test("should have responsive mobile menu", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto("/");

    await expect(page.locator('button[aria-label="open drawer"]')).toBeVisible();
  });
});
