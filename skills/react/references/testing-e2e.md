# End-to-End Testing

> Load when: end-to-end or full-browser tests, Playwright. Pinned: React 19.3, Vite 8, React Compiler 1.0, React Router 8.

## Existing repo
- How to recognise it: `@playwright/test` in `package.json`, `playwright.config.ts`, an `e2e/` folder or `*.spec.ts` files, or Cypress (`cypress.config.*`).
- Rule: follow what is there. Never migrate Cypress to Playwright unasked.

## New repo default
- Playwright Test (`@playwright/test`); scaffold with `npm init playwright@latest`. The install page lists the supported Node versions.
- `webServer` in `playwright.config.ts` starts the Vite dev server (or `vite preview` after a build in CI); set `baseURL` so tests use relative URLs; `reuseExistingServer: !process.env.CI`.
- Role-based locators first (`getByRole`, then `getByText`, `getByLabel`); test ids as a contract; CSS/XPath last.
- Web-first assertions that auto-wait: `await expect(locator).toBeVisible()`.
- Auth reuse: a `setup` project logs in once and saves `storageState` to `playwright/.auth/user.json` (git-ignored); browser projects depend on it.
- Mock the network with `page.route` only for third-party calls; your own API runs for real.
- Each test is isolated (own context, own data); test user-visible behaviour only.

```ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  use: { baseURL: 'http://localhost:5173' },
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
  },
  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'], storageState: 'playwright/.auth/user.json' },
      dependencies: ['setup'],
    },
  ],
});
```

The setup file (`e2e/auth.setup.ts`) logs in through the UI, then calls `page.context().storageState({ path: authFile })`.

## Avoid
- `page.waitForTimeout` → arbitrary sleeps are flaky → web-first assertions or `locator.waitFor`.
- CSS/XPath chains when a role locator exists → break on DOM change → `getByRole`.
- `expect(await locator.isVisible()).toBe(true)` → returns immediately, no retry → `await expect(locator).toBeVisible()`.
- Logging in through the UI in every test → slow → `storageState` setup project.
- Committing `playwright/.auth` → holds session data → add it to `.gitignore`.
- Testing third-party pages or links → outside your control → `page.route` to stub them.

## Sources
- https://playwright.dev/docs/intro (fetched 2026-10-08)
- https://playwright.dev/docs/best-practices (fetched 2026-10-08)
- https://playwright.dev/docs/locators (fetched 2026-10-08)
- https://playwright.dev/docs/auth (fetched 2026-10-08)
- https://playwright.dev/docs/test-webserver (fetched 2026-10-08)
