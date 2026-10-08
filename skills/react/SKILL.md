---
name: react
description: React single-page apps on Vite — components, hooks and effects, performance and React Compiler, error boundaries, accessibility, state (Context, Zustand, Redux Toolkit, Jotai), server state (TanStack Query, SWR, RTK Query), forms (React Hook Form, TanStack Form, Zod), routing (React Router, TanStack Router), styling (Tailwind, CSS Modules, CSS-in-JS, shadcn/ui, MUI, Mantine, Chakra), Vite config, React Testing Library, MSW, Storybook, Playwright, i18n, OIDC auth, and class-component / Create React App legacy. Use when writing, reviewing, styling or testing .jsx/.tsx components or editing vite.config. Not for Next.js, Server Components, React Router framework mode/Remix, React Native or Expo.
---

# React (Vite SPA)

Pinned: React 19.3, Vite 8 (Node 20.19+ or 22.12+), React Compiler 1.0, React Router 8. Client-side SPA only.
Out of scope: Next.js (`next` dependency, `app/` router), Server Components, server actions (client-side `useActionState`/`useOptimistic` are in scope), React Router framework mode (`@react-router/dev`, `react-router.config.ts`), Remix, React Native, Expo → say so, load no reference, stop.
Not a React task at all (plain TS/JS utilities, tsconfig, package manager, back-end code) → this skill doesn't apply: load nothing, skip Step 1.

## Step 1 — Mode check (always first)

1. `<repo root>/.claude/conventions/react.md` exists → read it. It overrides every default here and in references.
2. A `package.json` listing `react` exists (root or any app) but no conventions file → read `references/detect-conventions.md`, scan only the React app being edited (nearest `package.json` with `react`) plus the repo root — skip `node_modules`, build output and non-React apps or services — write the conventions file, show it to the user; after the user confirms it, continue to Step 2 for the original task.
3. No `package.json` listing `react` anywhere (new app) → read `references/choose-conventions.md`, let the user pick, write the conventions file; after the user picks and the file is written, continue to Step 2 for the original task.
4. Code you are touching contradicts the conventions file → before writing any code, tell the user, ask which wins, update the file; after the answer, continue to Step 2 for the original task.

Step 1 never replaces Step 2: after it, always route the original task.

## Step 2 — Route: read every row whose signal matches the task

| Task signal | Read |
|---|---|
| Writing or reviewing any function component, JSX/TSX, props, `children`, composition, refs, `forwardRef` | `references/components.md` |
| `useEffect`, custom hooks, rules of hooks, hooks in conditions, `use(...)`, Suspense for data, syncing state with props | `references/hooks-and-effects.md` |
| Slow renders, re-renders, `memo`/`useMemo`/`useCallback`, React Compiler, `lazy`, code splitting, bundle size, long lists, virtualization, `key` | `references/performance.md` |
| Crashes, fallback UI, error boundaries, `react-error-boundary` | `references/error-boundaries.md` |
| Accessibility, a11y, keyboard use, focus, ARIA, screen readers, modals/dialogs, `jsx-a11y` | `references/accessibility.md` |
| Shared or global client state, prop drilling, Context, Zustand, Redux Toolkit, Jotai | `references/state-management.md` |
| Fetching API data, caching, refetching, mutations, loading/error states for data, TanStack Query, SWR, RTK Query | `references/server-state.md` |
| Forms, inputs, form validation, submit handling, React Hook Form, TanStack Form, `useActionState`, `useOptimistic` | `references/forms.md` |
| Adding or changing routes (e.g. a new `/settings` URL), route params, navigation, links, search params or URL state, React Router, TanStack Router | `references/routing.md` |
| CSS, styling, theming, dark mode, Tailwind, CSS Modules, styled-components, Emotion, shadcn/ui, Radix, MUI, Mantine, Chakra | `references/styling.md` |
| `vite.config`, Vite plugins, `import.meta.env`, env variables, dev proxy, React lint rules (`eslint-plugin-react-hooks`, `eslint-plugin-react-refresh`) | `references/vite-and-lint.md` |
| Component tests, React Testing Library, `user-event`, jsdom, Vitest browser mode, MSW API mocks, Storybook stories | `references/testing-components.md` |
| End-to-end or full-browser tests, Playwright | `references/testing-e2e.md` |
| Translations, locales, i18n, react-i18next, FormatJS / react-intl | `references/i18n.md` |
| Login, logout, tokens, OIDC, OAuth, PKCE, protected pages or routes | `references/auth-spa.md` |
| Class components, lifecycle methods (`componentDidMount`, `componentDidUpdate`), `react-scripts`, Create React App, migrating to Vite | `references/legacy-migration.md` |

Several rows match → read each. No row matches → use the always-rules only; never read references speculatively.

## Always-rules

- New code: function components + hooks (error boundaries: `react-error-boundary`). Existing class components stay unless the user asks to migrate.
- Call hooks only at the top level of components and custom hooks (the `use` API is the one exception).
- Derive values during render; use effects only to sync with external systems.
- Server data goes through the conventions file's `server-state` choice; a repo that fetches in effects keeps that style unless asked. Never mirror fetched data into a separate global store.
- Stable, unique `key`s; never the array index unless the list is static.
- Existing repo: keep its libraries; never migrate one unasked. New repo: use the user-approved defaults from the choose-conventions reference.
