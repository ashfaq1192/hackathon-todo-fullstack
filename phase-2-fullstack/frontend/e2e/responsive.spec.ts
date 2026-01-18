// E2E test for responsive design at multiple viewports
// T081 [P] [US8]

import { test, expect } from '@playwright/test';

// Define common viewports to test
const viewports = {
  mobile: { width: 375, height: 667 }, // iPhone SE
  tablet: { width: 768, height: 1024 }, // iPad
  desktop: { width: 1440, height: 900 }, // Common desktop
};

test.describe('Responsive Design', () => {
  // Log in a user before all tests to ensure we are on the dashboard
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="email"]', 'testuser@example.com');
    await page.fill('input[name="password"]', 'CorrectPassword123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/tasks');
  });

  // Iterate over viewports for responsiveness tests
  for (const device in viewports) {
    const { width, height } = viewports[device as keyof typeof viewports];

    test(`should display correct layout on ${device} (${width}x${height})`, async ({ page }) => {
      await page.setViewportSize({ width, height });
      await page.reload(); // Reload to apply viewport changes correctly

      // Test Navigation component responsiveness
      if (width < 768) { // Assuming a breakpoint for mobile navigation
        // Check for hamburger menu (if implemented)
        // await expect(page.locator('[data-testid="hamburger-menu"]')).toBeVisible();
        // Check that full navigation links are hidden
        // await expect(page.locator('[data-testid="desktop-nav-links"]')).toBeHidden();
      } else {
        // Check that full navigation links are visible
        // await expect(page.locator('[data-testid="desktop-nav-links"]')).toBeVisible();
        // Check that hamburger menu is hidden
        // await expect(page.locator('[data-testid="hamburger-menu"]')).toBeHidden();
      }

      // Check CreateTaskForm responsiveness (e.g., full width on mobile, constrained on desktop)
      const createTaskForm = page.locator('form h2:has-text("Add a New Task")');
      await expect(createTaskForm).toBeVisible();
      const formBoundingBox = await createTaskForm.boundingBox();
      expect(formBoundingBox?.width).toBeLessThanOrEqual(width); // Should not overflow

      // Check TaskList and TaskItem responsiveness
      const taskList = page.locator('.space-y-4'); // Assuming TaskList's root element
      await expect(taskList).toBeVisible();
      const taskListBoundingBox = await taskList.boundingBox();
      expect(taskListBoundingBox?.width).toBeLessThanOrEqual(width);

      // Verify no horizontal scrollbar
      const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
      expect(scrollWidth).toBeLessThanOrEqual(width);
    });
  }
});
