# Testing Components

> Load when: component tests, React Testing Library, `user-event`, jsdom, Vitest browser mode, MSW API mocks, Storybook stories. Pinned: React 19.3, Vite 8, React Compiler 1.0, React Router 8.

## Existing repo
- How to recognise it: `@testing-library/react` in `package.json`, `*.test.tsx` files, a `setupTests`/`vitest.setup` file, an `msw` handlers folder, `.storybook/`, Jest or Vitest config.
- Rule: follow what is there (runner, query style, mocking). Add Storybook stories only if the repo already uses Storybook or the user asks. Test-runner setup belongs to the typescript skill.

## New repo default
- Vitest + jsdom + React Testing Library + `@testing-library/user-event`; test what a user sees and does, not state or instance methods.
- Query priority: `getByRole` first (with `name`), then `getByLabelText`, `getByPlaceholderText`, `getByText`, `getByDisplayValue`, `getByAltText`/`getByTitle`; `getByTestId` last.
- `getBy*` for present elements, `queryBy*` to assert absence, `findBy*` (async, retries) for elements that appear later.
- Call `userEvent.setup()` before `render`, inside the test (not in `beforeEach`); `await` every `user.*` call.
- MSW for API mocks: handlers in one module, `setupServer` (from `msw/node`) in tests, the same handlers in `setupWorker` for the dev worker. Do not stub `fetch` by hand.
- Test setup file: `server.listen()` before all, `server.resetHandlers()` after each, `server.close()` after all.
- DOM matchers (`toBeVisible`, `toBeInTheDocument`) come from `@testing-library/jest-dom`: import `@testing-library/jest-dom/vitest` in the test setup file.
- `renderWithProviders` wraps a fresh `QueryClient` (retries off) and a router; tests import it instead of `render`.
- Vitest browser mode (real browser instead of jsdom) is the alternative: needs an explicit `browser` config, a provider (Playwright is the recommended one) and `vitest-browser-react`. The browser guide page carries no experimental/stable label, so check it before choosing.
- Storybook (only when used): one CSF story per variant (`Meta`, `StoryObj`); MSW handlers can be reused in stories.

```tsx
import { expect, test } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { createMemoryRouter, RouterProvider } from 'react-router';
import type { ReactElement } from 'react';

export function renderWithProviders(ui: ReactElement, route = '/') {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  const router = createMemoryRouter([{ path: '*', element: ui }], { initialEntries: [route] });
  return render(
    <QueryClientProvider client={client}>
      <RouterProvider router={router} />
    </QueryClientProvider>,
  );
}

test('saves the profile', async () => {
  const user = userEvent.setup();
  renderWithProviders(<ProfileForm />);
  await user.type(screen.getByLabelText(/name/i), 'Ada');
  await user.click(screen.getByRole('button', { name: /save/i }));
  expect(await screen.findByText(/saved/i)).toBeVisible();
});
```

## Avoid
- Asserting on state, props or instance methods → breaks on refactor → assert rendered output and behaviour.
- Snapshot-only tests → pass without checking behaviour → explicit assertions on roles and text.
- `getByTestId` first or CSS selectors → not what users perceive → `getByRole`.
- Hand-mocked `fetch` or `axios` → drifts from the real API shape → MSW handlers.
- `user-event` calls without `await`, or created in hooks → flaky, nested setup → `userEvent.setup()` in the test.

## Sources
- https://testing-library.com/docs/react-testing-library/intro (fetched 2026-10-08)
- https://testing-library.com/docs/queries/about#priority (fetched 2026-10-08)
- https://testing-library.com/docs/user-event/intro (fetched 2026-10-08)
- https://vitest.dev/guide/browser/ (fetched 2026-10-08)
- https://mswjs.io/docs (fetched 2026-10-08); https://mswjs.io/docs/quick-start (fetched 2026-10-08)
- https://storybook.js.org/docs (fetched 2026-10-08)
- https://github.com/testing-library/jest-dom (fetched 2026-10-08)
