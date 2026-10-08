---
name: typescript
description: TypeScript and JavaScript language and tooling — code style, type design, tsconfig and ESM/CommonJS modules, async patterns, error handling, runtime validation (Zod, Valibot, ArkType), JSDoc-typed JavaScript, project structure, package managers and monorepos (pnpm, npm, yarn, bun, Turborepo, Nx), ESLint, Biome, Prettier, Vitest, Jest, node:test, and build/run tools (tsc, tsup, tsdown, esbuild, tsx). Use when writing, reviewing, structuring, testing or building .ts/.js/.mts/.cts files, or editing tsconfig.json or package.json. Not for React/UI components or Node back-end frameworks (NestJS, Express, Fastify, Hono).
---

# TypeScript / JavaScript

Pinned: TypeScript 7.0.2 (stable native compiler), Node 24 LTS (type stripping on by default). Language + tooling only.
Out of scope: React/UI components, Node back-end framework APIs (NestJS, Express, Fastify, Hono routing, middleware, controllers) → handle only the TS/JS part (types, validation, tests) and say the framework part is out of scope; a purely out-of-scope task → say so, load no reference, stop.
Not a TS/JS code or tooling task at all → this skill doesn't apply: load nothing, skip Step 1.

## Step 1 — Mode check (always first)

1. `<repo root>/.claude/conventions/typescript.md` (one per repo; per-package differences are noted inside it) exists → read it. It overrides every default here and in references.
2. Any `package.json` or `tsconfig.json` in the repo (root or any package) but no conventions file → read `references/detect-conventions.md`, scan only the package being edited (nearest `package.json`) plus the repo root — skip `node_modules`, build output and unrelated apps — write the conventions file, show it to the user; after the user confirms it, continue to Step 2 for the original task.
3. None anywhere (new repo or empty folder) → read `references/choose-conventions.md`, let the user pick, write the conventions file; after the user picks and the file is written, continue to Step 2 for the original task.
4. Code you are touching contradicts the conventions file → stop, tell the user, ask which wins, update the file. In a monorepo, ask whether the difference is a per-package exception (add a `packages:` note) or a repo-wide change.

Step 1 never replaces Step 2: once the conventions file is settled, always route the original task through Step 2 as well.

## Step 2 — Route: read every row whose signal matches the task

| Task signal | Read |
|---|---|
| Writing or reviewing any TS/JS code | `references/ts-style.md` |
| Scaffolding a new project or package, `tsconfig.json`, compiler options, global types, `@types/*`, "Cannot find name 'process'", ESM vs CommonJS, `import`/`require` errors, `"type": "module"`, `moduleResolution`, path aliases | `references/tsconfig.md` |
| Designing types or interfaces, unions, generics, `any`/`unknown`, narrowing, type errors | `references/type-patterns.md` |
| `async`/`await`, promises, parallel work, timeouts, retries, cancellation, `AbortController` | `references/async.md` |
| `try`/`catch`, custom errors, error flow, Result types, neverthrow | `references/error-handling.md` |
| Parsing untrusted data (request body, env vars, JSON, config files), schemas, Zod, Valibot, ArkType | `references/runtime-validation.md` |
| Plain `.js` files, JSDoc types, `checkJs`, types without converting to TS | `references/javascript-jsdoc.md` |
| Scaffolding a new project or package, new module or folder, moving files, folder layout, `index.ts` barrel files | `references/project-structure.md` |
| Installing or adding dependencies, lockfiles, pnpm/npm/yarn/bun, workspaces, Turborepo, Nx | `references/packages-and-monorepo.md` |
| Scaffolding a new project or package, ESLint, typescript-eslint, Biome, oxlint, Prettier, lint/format config, husky, lefthook, lint-staged, pre-commit hooks | `references/lint-format.md` |
| Scaffolding a new project or package, writing or running tests, Vitest, Jest, `node:test`, mocks | `references/testing.md` |
| Scaffolding a new project or package, building, bundling or running TS, `tsx`, type stripping, `tsc`, tsup, tsdown, esbuild, CI type-check, publishing a package | `references/build-and-run.md` |

Several rows match → read each. No row matches → use the always-rules only; never read references speculatively.

## Always-rules

- `strict` on. No `any` — use `unknown` and narrow. No `@ts-ignore`; use `@ts-expect-error` with a reason.
- Await or explicitly handle every promise; no floating promises.
- Validate untrusted data at the boundary; trust the types inside.
- Type-stripping runners and bundlers do not type-check → `tsc --noEmit` must run in CI.
- New repo: use the user-approved defaults from the choose-conventions reference. Existing repo: keep its tools; never migrate one unasked.
