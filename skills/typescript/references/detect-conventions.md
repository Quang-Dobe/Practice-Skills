# Detect conventions (existing repo)

> Load when: a `package.json` or `tsconfig.json` exists in the repo (root or any package) but `<repo root>/.claude/conventions/typescript.md` does not. Pinned: TypeScript 7.0.2, Node 24 LTS (2026-10-04).

## Existing repo
- Goal: infer the repo's conventions from files, write ONE conventions file at `<repo root>/.claude/conventions/typescript.md`, get the user's confirmation.
- Scope: the package being edited (nearest `package.json`) plus the repo root. In a monorepo, record packages that differ from the root as `packages:` notes inside the single file, not as extra files.
- Skip: `node_modules`, `dist`, `build`, `.next`-style output, and apps unrelated to the task.
- Signal to field map. Each field is decided on its own: within one field, the first matching row wins; conflicting signals for one field, or no signal, mean ask the user, never guess:

| Signal | Field and value |
|---|---|
| `pnpm-lock.yaml` / `package-lock.json` / `yarn.lock` / `bun.lock` or `bun.lockb` | `package-manager`: pnpm / npm / yarn / bun |
| `package.json` `"type": "module"` | `module: esm` |
| `"type": "commonjs"` or absent | `module: cjs` (a `.mts`-only or bundler repo: note it) |
| `.js`/`.mjs` sources with `checkJs`/`allowJs` in `tsconfig.json` or `jsconfig.json`, or `// @ts-check` at file tops (even if a `tsconfig.json` exists) | `language: js-jsdoc` |
| `.ts` sources exist (a `tsconfig.json` alone is not enough) | `language: ts` |
| `eslint.config.*` / `.eslintrc*` / `biome.json` / `.oxlintrc.json` / `.prettierrc*` | `lint-format`: combine what exists, e.g. `eslint+prettier`, `biome` |
| `vitest.config.*` / `jest.config.*` / a `node --test` script | `test`: vitest / jest / node:test |
| `tsup.config.*` / `tsdown.config.*` / esbuild scripts / a `tsc` build script / `tsx` in scripts | `build-run`: tool + runner |
| `pnpm-workspace.yaml` / `turbo.json` / `nx.json` / `workspaces` in `package.json` | note "monorepo" |
| `src/<feature>/` folders vs `src/{controllers,services,utils}/` | `layout`: feature / layer |
| imports of `neverthrow` | `error-style: result`, otherwise `exceptions` |
| `zod` / `valibot` / `arktype` in dependencies | `validation`: that library, else `none` |
| a library with `exports` / `types` fields and no app entry; `bin` field; app-only | `project-type`: library / cli / app-package / mixed |

- `naming`: `default` unless the code or lint config shows deviations (record them).
- Write the file in this exact format. Create `.claude/conventions/` first if it is missing. Fill `detected-from` with the files you actually read. Set `mode: existing` and `updated` to today.

```
---
stack: typescript
mode: existing
updated: YYYY-MM-DD
detected-from: [package.json, pnpm-lock.yaml, tsconfig.json]
---
project-type: library
language: ts
module: esm
package-manager: pnpm
lint-format: eslint+prettier
test: vitest
build-run: tsup + tsx
layout: feature
error-style: exceptions
validation: zod
naming: default
packages: <optional — per-package differences in a monorepo, e.g. "packages/legacy: cjs, jest">
```

- Then show the file to the user and wait for confirmation or corrections before the original task continues.

## New repo default
- Not applicable: an empty repo goes through the choose-conventions flow. If detection finds nothing usable, say so and ask the user instead of defaulting silently.

## Avoid
- Writing the file without showing it → the user cannot correct a wrong guess → show it and wait.
- Scanning `node_modules` or build output → misleading signals and slow → stay in scope.
- Reading a lockfile's contents → large and unneeded → its filename is the signal.
- Migrating tools you detected → existing tooling is kept → only record it.
- Several conflicting lockfiles → ambiguous → ask which the user runs.

## Sources
- https://docs.npmjs.com/cli/configuring-npm/package-json (fetched 2026-10-04; `type` field, `workspaces` field)
- https://nodejs.org/api/packages.html (fetched 2026-10-04; `"type"` decides how `.js` is interpreted)
- https://pnpm.io/workspaces (fetched 2026-10-04; `pnpm-workspace.yaml` marks a pnpm monorepo)
