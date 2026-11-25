import { defineConfig, devices } from '@playwright/test';
export default defineConfig({
  testDir: './tests', testMatch: 'site.spec.mjs', timeout: 30000,
  use: { baseURL: 'http://127.0.0.1:4174', browserName: 'chromium' },
  globalSetup: './tests/serve.mjs',
  projects: [ { name: 'desktop', use: { viewport: { width: 1440, height: 1000 } } }, { name: 'mobile', use: { ...devices['iPhone 13'], defaultBrowserType: 'chromium' } } ]
});
