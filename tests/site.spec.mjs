import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
test('semantic resume, metadata, responsive layout and accessibility', async ({ page }, testInfo) => {
  const remote = [];
  page.on('request', request => { if (!request.url().startsWith('http://127.0.0.1:4174')) remote.push(request.url()); });
  const response = await page.goto('/');
  expect(response.status()).toBe(200);
  await expect(page.getByRole('heading', { name: 'Kevwe Akpoguma' })).toBeVisible();
  for (const name of ['Experience', 'Technical expertise', 'Education', 'ResumeOps']) await expect(page.getByRole('heading', { name, exact: true })).toBeVisible();
  await expect(page.locator('#deployment')).toHaveText('Local preview · no deployment evidence');
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  expect(remote).toEqual([]);
  expect((await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze()).violations).toEqual([]);
  await page.screenshot({ path: `test-results/${testInfo.project.name}.png`, fullPage: true });
});
test('keyboard skip navigation and reduced motion', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto('/');
  await page.keyboard.press('Tab');
  await expect(page.getByRole('link', { name: 'Skip to content' })).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.locator('main')).toBeFocused();
  expect(await page.evaluate(() => getComputedStyle(document.documentElement).scrollBehavior)).toBe('auto');
});
test('deployment metadata is text-only and fails safely', async ({ page }) => {
  await page.route('**/deployment.json', route => route.fulfill({ json: { sha: 'a'.repeat(40), date: '2026-11-25T12:00:00Z' } }));
  await page.goto('/');
  await expect(page.locator('#deployment')).toHaveText('Content revision aaaaaaaaaaaa · deployed 2026-11-25T12:00:00.000Z');
  await page.route('**/deployment.json', route => route.fulfill({ json: { sha: '<script>alert(1)</script>', date: 'invalid' } }));
  await page.reload();
  await expect(page.locator('#deployment')).toHaveText('Local preview · no deployment evidence');
});
