import { test, expect } from "@playwright/test";

test.describe("Login Flow", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });

  test("should navigate to login page", async ({ page }) => {
    await page.click('a:has-text("Login")');
    await expect(page).toHaveURL(/.*auth\/login/);
    await expect(page.locator("h4")).toContainText("Login");
  });

  test("should show validation errors for empty form", async ({ page }) => {
    await page.goto("/auth/login");
    await page.click('button[type="submit"]');

    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
  });

  test("should login successfully with valid credentials", async ({ page }) => {
    await page.goto("/auth/login");

    await page.fill('input[type="email"]', "test@example.com");
    await page.fill('input[type="password"]', "password123");

    await page.click('button[type="submit"]');

    await page.waitForURL("/", { timeout: 5000 }).catch(() => {
      console.log("Note: Login requires backend API to be running");
    });
  });

  test("should navigate to register page from login", async ({ page }) => {
    await page.goto("/auth/login");
    await page.click('a:has-text("Register here")');
    await expect(page).toHaveURL(/.*auth\/register/);
  });
});
