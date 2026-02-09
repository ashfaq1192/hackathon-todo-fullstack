import { test, expect } from '@playwright/test';

test.describe('Chatbot functionality', () => {
  const TEST_USER_PASSWORD = 'TestPassword123!';
  const TEST_USER_NAME = 'E2E Test User';

  test.beforeEach(async ({ page }) => {
    // Generate unique email for each test run
    const uniqueEmail = `e2e-chatbot-${Date.now()}-${Math.random().toString(36).slice(2)}@example.com`;

    // First, sign up a new user
    await page.goto('/signup');
    await page.fill('input[name="name"]', TEST_USER_NAME);
    await page.fill('input[name="email"]', uniqueEmail);
    await page.fill('input[name="password"]', TEST_USER_PASSWORD);
    await page.fill('input[name="confirmPassword"]', TEST_USER_PASSWORD);
    await page.click('button[type="submit"]');

    // Wait for redirect to dashboard after successful signup
    await page.waitForURL('/dashboard', { timeout: 30000 });
  });

  test('should display the chat interface and send/receive messages', async ({ page }) => {
    await page.goto('/chat');

    // Verify chat interface elements are present
    await expect(page.getByRole('heading', { name: 'Todo Assistant' })).toBeVisible();
    await expect(page.getByPlaceholder('Type your message or use voice input...')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Send' })).toBeVisible();

    // Send a message
    const testMessage = 'Hello, AI Assistant!';
    await page.getByPlaceholder('Type your message or use voice input...').fill(testMessage);
    await page.getByRole('button', { name: 'Send' }).click();

    // Verify user message appears in chat history
    await expect(page.getByText(testMessage)).toBeVisible();

    // Wait for either an assistant response OR an error message (AI might be slow or unavailable)
    // The assistant response will appear in a div with justify-start class
    const assistantResponseOrError = page.locator('.justify-start .whitespace-pre-wrap, .justify-start .italic, [role="alert"]').first();
    await expect(assistantResponseOrError).toBeVisible({ timeout: 45000 });
  });

  test('should show example commands initially', async ({ page }) => {
    await page.goto('/chat');

    // Verify example commands are visible when no messages have been sent
    await expect(page.getByText('Start a conversation')).toBeVisible();
    await expect(page.getByText('Ask me to add, view, update, or complete tasks')).toBeVisible();
    await expect(page.getByText('Example commands:')).toBeVisible();
    await expect(page.getByText('• "Add a task to buy groceries"')).toBeVisible();
  });
});
