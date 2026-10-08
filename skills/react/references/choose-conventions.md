# Choose Conventions

> Load when: no `package.json` listing `react` exists anywhere (new app). Pinned: React 19.3, Vite 8, React Compiler 1.0, React Router 8.

## Existing repo
- How to recognise it: this file applies only to an empty or React-free repo; any `package.json` with `react` means use the detect-conventions reference instead.
- Rule: follow what is there.

## New repo default
Defaults chosen by the user (2026-10-07). Show the menu, recommended first; wait for the user's picks.

| Area | Recommended | Alternatives |
|---|---|---|
| Scaffold | Vite `react-ts` template + `@vitejs/plugin-react` | `@vitejs/plugin-react-swc` |
| React Compiler | on; no manual `memo`/`useMemo`/`useCallback` | off (manual memo) |
| Router | React Router 8, data mode (`createBrowserRouter`) | TanStack Router |
| Server state | TanStack Query | SWR; RTK Query if Redux present |
| Client state | none until needed, then Zustand | Redux Toolkit, Jotai |
| Forms | React Hook Form + Zod | TanStack Form |
| Styling + UI kit | Tailwind CSS + shadcn/ui | CSS Modules; MUI, Mantine |
| Component tests + mocks | Vitest + jsdom + Testing Library + `user-event` + MSW | Vitest browser mode |
| E2E | Playwright | none |
| i18n | react-i18next | FormatJS (react-intl) |
| Auth | `oidc-client-ts` + `react-oidc-context`, auth code + PKCE, tokens in memory | BFF cookie pattern |
| Layout | feature folders `src/features/<name>/` | layer folders |

- Scaffold: `npm create vite@latest <name> -- --template react-ts`. The Vite guide requires Node 20.19+ or 22.12+. The package manager is the typescript skill's call.
- Compiler (plugin-react 6.0.0+): `npm install -D babel-plugin-react-compiler @rolldown/plugin-babel @babel/core`, then add `babel({ presets: [reactCompilerPreset()] })` after `react()` (snippet below).
- Router: `npm install react-router`; mount `<RouterProvider router={router} />`.
- Tailwind: `npm install tailwindcss @tailwindcss/vite`. shadcn/ui: `npx shadcn@latest init` (its Vite guide shows the `pnpm dlx` form).
- After the user picks, write `<repo root>/.claude/conventions/react.md` with `mode: new` (recommended picks shown; replace each value with the user's pick). shadcn/ui is recorded as `styling: tailwind`. Show the file, get a yes, then continue with the original task.

```markdown
---
stack: react
mode: new
updated: YYYY-MM-DD
detected-from: []
---
react: 19   compiler: on
router: react-router-data
server-state: tanstack-query
client-state: none
forms: react-hook-form
styling: tailwind
tests: rtl+jsdom   mocks: msw   e2e: playwright
i18n: react-i18next
layout: feature
```

```ts
// vite.config.ts
import { defineConfig } from 'vite';
import react, { reactCompilerPreset } from '@vitejs/plugin-react';
import babel from '@rolldown/plugin-babel';

export default defineConfig({
  plugins: [react(), babel({ presets: [reactCompilerPreset()] })],
});
```

## Avoid
- Choosing for the user → defaults are recommendations → show the menu and wait.
- Adding a global store up front → extra state with no need → start with none, add Zustand when state is shared.
- Next.js, framework-mode React Router, Create React App → out of scope or not recommended → Vite SPA.

## Sources
- https://vite.dev/guide/ (fetched 2026-10-08)
- https://react.dev/learn/creating-a-react-app (fetched 2026-10-08)
- https://react.dev/learn/react-compiler/installation (fetched 2026-10-08)
- https://reactrouter.com/home (fetched 2026-10-08)
- https://tanstack.com/query/latest (fetched 2026-10-08)
- https://zustand.docs.pmnd.rs/ (fetched 2026-10-08)
- https://react-hook-form.com/ (fetched 2026-10-08)
- https://tailwindcss.com/docs/installation/using-vite (fetched 2026-10-08)
- https://ui.shadcn.com/docs/installation/vite (fetched 2026-10-08)
- https://testing-library.com/docs/react-testing-library/intro/ (fetched 2026-10-08)
- https://mswjs.io/docs/ (fetched 2026-10-08)
- https://playwright.dev/docs/intro (fetched 2026-10-08)
- https://react.i18next.com/ (fetched 2026-10-08)
- https://authts.github.io/oidc-client-ts/ (fetched 2026-10-08)
- https://github.com/authts/react-oidc-context (fetched 2026-10-08)
