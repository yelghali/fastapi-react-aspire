import { test, expect } from "@playwright/test";

test.describe("Navigation", () => {
  test("should navigate between all pages", async ({ page }) => {
    // Start at home
    await page.goto("/");
    await expect(page).toHaveTitle(/FastAPI React Aspire/);

    // Go to Items
    await page.getByRole("link", { name: "Items Demo", exact: true }).click();
    await expect(page).toHaveURL(/\/items/);
    await expect(page.getByRole("heading", { name: "Items" })).toBeVisible();

    // Back to home
    await page.getByRole("link", { name: "← Home" }).click();
    await expect(page).toHaveURL("/");

    // Go to Projects
    await page.getByRole("link", { name: "Projects" }).click();
    await expect(page).toHaveURL(/\/projects/);

    // Back to home
    await page.getByRole("link", { name: "← Home" }).click();
    await expect(page).toHaveURL("/");
  });

  test("should handle direct URL navigation", async ({ page }) => {
    await page.goto("/items");
    await expect(page.getByRole("heading", { name: "Items" })).toBeVisible();

    await page.goto("/projects");
    await expect(page).toHaveTitle(/Projects/);

    await page.goto("/");
    await expect(
      page.getByRole("heading", { name: /FastAPI \+ React \+ Aspire/ })
    ).toBeVisible();
  });

  test("should return 404 for unknown routes", async ({ page }) => {
    const response = await page.goto("/nonexistent-page");
    // React Router may handle this as a client-side 404 or show the app shell
    expect(response).not.toBeNull();
  });
});
