# Detect Conventions

> Load when: a `package.json` listing `react` exists but there is no `<repo root>/.claude/conventions/react.md`. Pinned: React 19.3, Vite 8, React Compiler 1.0, React Router 8.

## Existing repo
- Scope: the React app being edited (nearest `package.json` with `react`) plus the repo root. Skip `node_modules`, `dist`/`build` and non-React apps or services.
- Read `package.json` (`dependencies` + `devDependencies`), `vite.config.*`, and the top two levels of `src/`. Record every file actually read in `detected-from`.
- Map signals to fields:

| Signal | Field value |
|---|---|
| `react` version in `package.json` | `react: <major>` |
| `babel-plugin-react-compiler`, or compiler preset/config in `vite.config.*` | `compiler: on`; absent → `off` |
| `react-router` or `react-router-dom` + `createBrowserRouter` | `router: react-router-data` |
| `react-router` or `react-router-dom` + `<BrowserRouter>` only | `router: react-router-declarative` |
| `@tanstack/react-router` | `router: tanstack-router`; no router → `none` |
| `@tanstack/react-query` / `swr` / `@reduxjs/toolkit` with `createApi` | `server-state: tanstack-query` / `swr` / `rtk-query` |
| none of those and `fetch` inside `useEffect` | `server-state: fetch-in-effects` |
| `zustand` / `@reduxjs/toolkit` / `jotai` | `client-state: zustand` / `redux-toolkit` / `jotai`; none → `none` (or `context` if app-wide Context holds state) |
| `react-hook-form` / `@tanstack/react-form` | `forms: react-hook-form` / `tanstack-form`; else `plain` |
| `tailwindcss`, `*.module.css`, `styled-components`, `@emotion/*`, `components.json` (shadcn), `@mui/material`, `@mantine/core`, `@chakra-ui/react` | `styling: tailwind` / `css-modules` / `styled-components` / `emotion` / the UI kit name |
| `@testing-library/react` + `jsdom`, or Vitest `browser` config | `tests: rtl+jsdom` / `rtl+browser-mode` |
| `msw` / `@playwright/test` | `mocks: msw` / `e2e: playwright`; else `none` |
| `react-i18next` / `react-intl` | `i18n: react-i18next` / `formatjs`; else `none` |
| `src/features/<name>/` vs `src/{components,hooks,pages}/` | `layout: feature` / `layer` |

- `react-scripts` dependency → write "CRA (legacy)" as a note in the file body; do not migrate.
- Write `<repo root>/.claude/conventions/react.md` (create `.claude/conventions/` if missing), then show it to the user and wait for confirmation. After confirmation, continue with the original task.
- Later mismatch: code you are about to touch contradicts the file → before writing any code, tell the user, ask which wins, update the file, then continue with the original task.
- Rule: follow what is there. Detection records the repo; it never changes it.

## New repo default
- Not applicable: a repo with no React dependency uses the choose-conventions reference instead.
- Where signals are missing or conflicting, state both readings to the user rather than guessing.

```markdown
---
stack: react
mode: existing
updated: 2026-10-08
detected-from: [package.json, vite.config.ts, src/]
---
react: 19   compiler: off
router: react-router-data
server-state: tanstack-query
client-state: none
forms: react-hook-form
styling: tailwind
tests: rtl+jsdom   mocks: msw   e2e: playwright
i18n: none
layout: feature
```

## Avoid
- Scanning `node_modules` or build output → noise and slow → read only manifests and config.
- Guessing a field with no signal → a wrong file overrides every default → use the closest allowed value (`none`/`plain`) and say so.
- Proposing upgrades while detecting (CRA to Vite, Router to v8) → unasked migration → record the fact only.

## Sources
- https://react.dev/learn/react-compiler (fetched 2026-10-08)
- https://react.dev/learn/react-compiler/installation (fetched 2026-10-08)
- https://reactrouter.com/start/modes (fetched 2026-10-08)
