import { test, expect } from "@playwright/test";

test.describe("Items Page", () => {
  test("should load the items page", async ({ page }) => {
    await page.goto("/items");
    await expect(page).toHaveTitle(/Items/);
    await expect(
      page.getByRole("heading", { name: "Items" })
    ).toBeVisible();
  });

  test("should have a back link to home", async ({ page }) => {
    await page.goto("/items");
    const homeLink = page.getByRole("link", { name: "← Home" });
    await expect(homeLink).toBeVisible();
    await homeLink.click();
    await expect(page).toHaveURL("/");
  });

  test("should display the create item form", async ({ page }) => {
    await page.goto("/items");
    await expect(page.getByPlaceholder("Item name")).toBeVisible();
    await expect(
      page.getByPlaceholder("Description (optional)")
    ).toBeVisible();
    await expect(
      page.getByRole("button", { name: /Add/ })
    ).toBeVisible();
  });

  test("should have a refresh button", async ({ page }) => {
    await page.goto("/items");
    await expect(
      page.getByRole("button", { name: "Refresh" })
    ).toBeVisible();
  });

  test("should show loading or empty state initially", async ({ page }) => {
    await page.goto("/items");
    // Should show either loading state, items, or empty state
    const hasContent = await page
      .locator("text=Loading...").or(page.locator("text=No items yet")).or(page.locator("text=ID:"))
      .first()
      .waitFor({ timeout: 10000 })
      .then(() => true)
      .catch(() => false);
    expect(hasContent).toBe(true);
  });

  test("should display the tip box", async ({ page }) => {
    await page.goto("/items");
    await expect(page.getByText(/Tip:/)).toBeVisible();
  });

  test("should require item name before submitting", async ({ page }) => {
    await page.goto("/items");
    const nameInput = page.getByPlaceholder("Item name");
    // The input has the required attribute, so submitting empty should not work
    await expect(nameInput).toHaveAttribute("required", "");
  });
});
