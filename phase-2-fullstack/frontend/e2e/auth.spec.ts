// E2E test for signup and login flows
// T032 [P] [US1] - Signup flow
// T041 [P] [US2] - Login flow

import { test, expect } from '@playwright/test';

test.describe('User Registration (Signup)', () => {
  test('should successfully sign up with valid credentials', async ({ page }) => {
    await page.goto('/signup');

    // Fill out signup form
    await page.fill('input[name="email"]', 'newuser@example.com');
    await page.fill('input[name="password"]', 'SecurePassword123');
    await page.fill('input[name="confirmPassword"]', 'SecurePassword123');

    // Submit form
    await page.click('button[type="submit"]');

    // Verify redirect to login page after successful signup
    await expect(page).toHaveURL('/login');

    // Verify success message (if implemented)
    // await expect(page.locator('text=Account created successfully')).toBeVisible();
  });

  test('should show error for duplicate email', async ({ page }) => {
    await page.goto('/signup');

    // Try to sign up with existing email
    await page.fill('input[name="email"]', 'existing@example.com');
    await page.fill('input[name="password"]', 'SecurePassword123');
    await page.fill('input[name="confirmPassword"]', 'SecurePassword123');

    await page.click('button[type="submit"]');

    // Verify error message
    await expect(page.locator('text=/email already (exists|registered|in use)/i')).toBeVisible();
  });

  test('should show error for weak password', async ({ page }) => {
    await page.goto('/signup');

    // Try to sign up with weak password (less than 8 characters)
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'weak');
    await page.fill('input[name="confirmPassword"]', 'weak');

    await page.click('button[type="submit"]');

    // Verify validation error
    await expect(page.locator('text=/password must be at least 8 characters/i')).toBeVisible();
  });

  test('should show error when passwords do not match', async ({ page }) => {
    await page.goto('/signup');

    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'SecurePassword123');
    await page.fill('input[name="confirmPassword"]', 'DifferentPassword123');

    await page.click('button[type="submit"]');

    // Verify validation error
    await expect(page.locator('text=/passwords do not match/i')).toBeVisible();
  });

  test('should show error for invalid email format', async ({ page }) => {
    await page.goto('/signup');

    await page.fill('input[name="email"]', 'invalid-email');
    await page.fill('input[name="password"]', 'SecurePassword123');
    await page.fill('input[name="confirmPassword"]', 'SecurePassword123');

    await page.click('button[type="submit"]');

    // Verify validation error
    await expect(page.locator('text=/invalid email address/i')).toBeVisible();
  });

  test('should disable submit button during form submission', async ({ page }) => {
    await page.goto('/signup');

    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'SecurePassword123');
    await page.fill('input[name="confirmPassword"]', 'SecurePassword123');

    // Click submit and immediately check if button is disabled
    const submitButton = page.locator('button[type="submit"]');
    await submitButton.click();

    // Verify loading state
    await expect(submitButton).toBeDisabled();
    await expect(page.locator('text=/signing up/i')).toBeVisible();
  });
});

test.describe('User Login', () => {
  test('should successfully log in with valid credentials', async ({ page }) => {
    await page.goto('/login');

    // Fill out login form
    await page.fill('input[name="email"]', 'testuser@example.com');
    await page.fill('input[name="password"]', 'CorrectPassword123');

    // Submit form
    await page.click('button[type="submit"]');

    // Verify redirect to tasks page after successful login
    await expect(page).toHaveURL('/tasks');

    // Verify JWT is stored (check for authenticated UI elements)
    await expect(page.locator('text=testuser@example.com')).toBeVisible();
  });

  test('should show error for invalid password', async ({ page }) => {
    await page.goto('/login');

    await page.fill('input[name="email"]', 'testuser@example.com');
    await page.fill('input[name="password"]', 'WrongPassword123');

    await page.click('button[type="submit"]');

    // Verify error message
    await expect(page.locator('text=/invalid (credentials|password)/i')).toBeVisible();
  });

  test('should show error for non-existent email', async ({ page }) => {
    await page.goto('/login');

    await page.fill('input[name="email"]', 'nonexistent@example.com');
    await page.fill('input[name="password"]', 'SomePassword123');

    await page.click('button[type="submit"]');

    // Verify error message
    await expect(page.locator('text=/(account not found|user does not exist|invalid credentials)/i')).toBeVisible();
  });

  test('should show error for invalid email format', async ({ page }) => {
    await page.goto('/login');

    await page.fill('input[name="email"]', 'invalid-email');
    await page.fill('input[name="password"]', 'SomePassword123');

    await page.click('button[type="submit"]');

    // Verify validation error
    await expect(page.locator('text=/invalid email address/i')).toBeVisible();
  });

  test('should disable submit button during form submission', async ({ page }) => {
    await page.goto('/login');

    await page.fill('input[name="email"]', 'testuser@example.com');
    await page.fill('input[name="password"]', 'CorrectPassword123');

    const submitButton = page.locator('button[type="submit"]');
    await submitButton.click();

    // Verify loading state
    await expect(submitButton).toBeDisabled();
    await expect(page.locator('text=/logging in/i')).toBeVisible();
  });

  test('should persist session after page reload', async ({ page }) => {
    // First, log in
    await page.goto('/login');
    await page.fill('input[name="email"]', 'testuser@example.com');
    await page.fill('input[name="password"]', 'CorrectPassword123');
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL('/tasks');

    // Reload the page
    await page.reload();

    // Verify still authenticated (not redirected to login)
    await expect(page).toHaveURL('/tasks');
    await expect(page.locator('text=testuser@example.com')).toBeVisible();
  });
});
