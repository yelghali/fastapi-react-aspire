import { test, expect } from "@playwright/test";

test.describe("Projects Page", () => {
  test("should load the projects page", async ({ page }) => {
    await page.goto("/projects");
    await expect(page).toHaveTitle(/Projects/);
  });

  test("should have a back link to home", async ({ page }) => {
    await page.goto("/projects");
    const homeLink = page.getByRole("link", { name: "← Home" });
    await expect(homeLink).toBeVisible();
    await homeLink.click();
    await expect(page).toHaveURL("/");
  });

  test("should have a refresh button", async ({ page }) => {
    await page.goto("/projects");
    await expect(
      page.getByRole("button", { name: "Refresh" })
    ).toBeVisible();
  });
});
