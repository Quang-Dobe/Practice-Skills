# Vite and React lint

> Load when: `vite.config`, Vite plugins, `import.meta.env`, env variables, dev proxy, React lint rules (`eslint-plugin-react-hooks`, `eslint-plugin-react-refresh`). Pinned: React 19.3, Vite 8, React Compiler 1.0, React Router 8.

## Existing repo
- How to recognise it: `vite.config.ts|js`; `@vitejs/plugin-react` or `@vitejs/plugin-react-swc` in `package.json`; `.env*` files; `eslint.config.*`.
- Keep the plugin in use. `@vitejs/plugin-react-swc` also supports React Compiler (`react({ compiler: true })`), but its README recommends the default plugin for most uses; do not swap unasked.
- Keep the existing env, proxy and ESLint setup; add rules only on request or for new code.
- Rule: follow what is there.

## New repo default
- `@vitejs/plugin-react` 6.0.0+ plus React Compiler through Babel: `npm install -D @rolldown/plugin-babel @babel/core babel-plugin-react-compiler` (and `@types/babel__core` for TypeScript). The plugin docs: `babel({ presets: [reactCompilerPreset()] })`.
- `reactCompilerPreset` options: `compilationMode: 'annotation'` (compile only `"use memo"` code), `target: '17' | '18'` for older React.
- Env vars: read through `import.meta.env`; only `VITE_`-prefixed variables reach client code. Files: `.env`, `.env.local`, `.env.[mode]`; mode files beat generic ones, real process env beats both.
- Never put secrets in `VITE_*`: they are bundled into client source. Secrets stay on a backend.
- Type custom vars by augmenting `ImportMetaEnv` in `src/vite-env.d.ts`; that file must contain no `import`.
- Dev proxy: `server.proxy` forwards `/api` to the backend, avoiding CORS in dev only (production needs its own routing).
- Lint on top of the typescript skill's base config: `eslint-plugin-react-hooks` flat `recommended` (includes compiler-backed rules such as `purity`, `refs`, `set-state-in-effect`) and `eslint-plugin-react-refresh` `vite` config.

```ts
// vite.config.ts
import { defineConfig } from 'vite';
import react, { reactCompilerPreset } from '@vitejs/plugin-react';
import babel from '@rolldown/plugin-babel';

export default defineConfig({
  plugins: [react(), babel({ presets: [reactCompilerPreset()] })],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:3000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
});
```

```ts
// eslint.config.ts (React part; merge into the base config)
import reactHooks from 'eslint-plugin-react-hooks';
import { reactRefresh } from 'eslint-plugin-react-refresh';
import { defineConfig } from 'eslint/config';

export default defineConfig(reactHooks.configs.flat.recommended, reactRefresh.configs.vite());
```

```ts
// src/vite-env.d.ts
/// <reference types="vite/client" />
interface ImportMetaEnv { readonly VITE_API_URL: string }
interface ImportMeta { readonly env: ImportMetaEnv }
```

## Avoid
- API keys or tokens in `VITE_*` or `.env` shipped to the client → readable by anyone → backend or token exchange.
- Loading `.env` values in `vite.config` via `import.meta.env` → not available there → `loadEnv`.
- Adding `memo`/`useMemo`/`useCallback` to satisfy the compiler → the compiler memoizes → fix the lint rule's finding instead.
- Silencing `react-hooks/*` with `eslint-disable` → hides real bugs → restructure the code.
- Relying on `server.proxy` in production → it exists only in the dev server → configure the host or gateway.

## Sources
- https://vite.dev/config/ (fetched 2026-10-08)
- https://vite.dev/guide/env-and-mode (fetched 2026-10-08)
- https://vite.dev/config/server-options#server-proxy (fetched 2026-10-08)
- https://github.com/vitejs/vite-plugin-react (fetched 2026-10-08; setup text taken from the plugin-react and plugin-react-swc READMEs in that repo, fetched 2026-10-08)
- https://react.dev/reference/eslint-plugin-react-hooks (fetched 2026-10-08; flat preset name from the plugin README, fetched 2026-10-08)
- https://react.dev/learn/react-compiler/installation (fetched 2026-10-08; plugin-react 6.0.0+ setup)
- https://github.com/ArnaudBarre/eslint-plugin-react-refresh (fetched 2026-10-08)
