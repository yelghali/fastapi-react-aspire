import { test, expect } from "@playwright/test";

test.describe("Home Page", () => {
  test("should load and display the page title", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle(/FastAPI React Aspire/);
  });

  test("should display the main heading", async ({ page }) => {
    await page.goto("/");
    await expect(
      page.getByRole("heading", { name: /FastAPI \+ React \+ Aspire/ })
    ).toBeVisible();
  });

  test("should display the starter template header", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText("🚀 Starter Template")).toBeVisible();
  });

  test("should display feature cards", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText("FastAPI Backend", { exact: true })).toBeVisible();
    await expect(page.getByText("React Router v7", { exact: true })).toBeVisible();
    await expect(page.getByText(".NET Aspire", { exact: true })).toBeVisible();
  });

  test("should display quick start section", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText("Quick Start")).toBeVisible();
    await expect(page.getByText("aspire run")).toBeVisible();
  });

  test("should have navigation links", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("link", { name: "Items Demo", exact: true })).toBeVisible();
    await expect(page.getByRole("link", { name: "Projects", exact: true }).first()).toBeVisible();
    await expect(page.getByRole("link", { name: "API Docs" })).toBeVisible();
  });

  test("should navigate to Items page", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("link", { name: "Items Demo", exact: true }).click();
    await expect(page).toHaveURL(/\/items/);
    await expect(
      page.getByRole("heading", { name: "Items" })
    ).toBeVisible();
  });

  test("should navigate to Projects page", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("link", { name: "Projects" }).click();
    await expect(page).toHaveURL(/\/projects/);
  });
});
