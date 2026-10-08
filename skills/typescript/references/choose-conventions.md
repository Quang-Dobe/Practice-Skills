# Choose conventions (new repo)

> Load when: no `package.json` or `tsconfig.json` exists anywhere in the repo (new repo). Pinned: TypeScript 7.0.2, Node 24 LTS (2026-10-04).

## Existing repo
- How to recognise it: any `package.json` / `tsconfig.json` or a conventions file exists. Then this file does not apply; use the detect flow instead.
- Rule: follow what is there. Never migrate tools unasked.

## New repo default
Defaults chosen by the user (2026-10-04). Present one menu item per area, recommended default first, and wait for the user's picks. Do not scaffold before they answer.

| Area | Default (first) | Alternatives |
|---|---|---|
| project type | app-package | library, cli, mixed |
| package manager | pnpm | npm, yarn, bun |
| module system | ESM (`"type": "module"`); `moduleResolution: NodeNext` for code Node runs, `Bundler` for bundled code | cjs |
| lint/format | ESLint flat config + typescript-eslint, plus Prettier | biome, oxlint+prettier |
| test | Vitest | jest, node:test |
| build/run | `tsc --noEmit` in CI; Node type stripping to run (Node 24 default); `tsc` builds libraries (JS + `.d.ts`); tsdown when bundling is needed; `tsx` only when non-erasable syntax is unavoidable | esbuild |
| layout | feature folders, no deep barrels | layer folders |
| error style | exceptions for unexpected failures | result (neverthrow) |
| validation | Zod at boundaries | valibot, arktype, none |

- Version caveat to tell the user when they pick typescript-eslint: its documented supported range is `>=4.8.4 <6.1.0`, and the TypeScript 7.0 announcement says 7.0 has no stable programmatic API (planned for 7.1). The announcement documents this `package.json` form, which keeps TS 6 under the `typescript` name for typescript-eslint and TS 7 under another name. The user decides; Biome/oxlint avoid the question.

```json
{
  "devDependencies": {
    "@typescript/native": "npm:typescript@^7.0.2",
    "typescript": "npm:@typescript/typescript6@^6.0.2"
  }
}
```

- After the picks, create `<repo root>/.claude/conventions/typescript.md` (create `.claude/conventions/` if missing) in this format with `mode: new`, `detected-from: []`, and `updated` set to today:

```
---
stack: typescript
mode: new
updated: YYYY-MM-DD
detected-from: []
---
project-type: app-package
language: ts
module: esm
package-manager: pnpm
lint-format: eslint+prettier
test: vitest
build-run: tsc + node type stripping
layout: feature
error-style: exceptions
validation: zod
naming: default
packages: <optional — per-package differences in a monorepo, e.g. "packages/legacy: cjs, jest">
```

- Show the file, get a yes, then continue with the original task.
- Chosen tools get their config from the matching reference when the task reaches it, not from this menu.

## Avoid
- Picking silently for the user → defaults are a recommendation → ask, then write.
- Offering more than the listed areas → menu sprawl → keep it to nine items.
- Offering tsup for a new repo → unmaintained → tsdown (tsup stays in repos that already use it).
- Mixing pnpm with another lockfile → conflicting installs → one package manager.
- `Bundler` resolution for code Node runs directly → imports fail at runtime → `NodeNext`.

## Sources
- https://pnpm.io/ (fetched 2026-10-04; "a fast, disk space efficient package manager")
- https://typescript-eslint.io/ (fetched 2026-10-04; ESLint support for TypeScript)
- https://typescript-eslint.io/users/dependency-versions (fetched 2026-10-04; supported TypeScript range `>=4.8.4 <6.1.0`)
- https://prettier.io/ (fetched 2026-10-04; opinionated code formatter)
- https://vitest.dev/ (fetched 2026-10-04; Vite-native testing framework)
- https://zod.dev/ (fetched 2026-10-04; TypeScript-first schema validation, Zod 4 stable)
- https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/ (fetched 2026-10-04; 7.0 stable 2026-07-08, no stable API until 7.1)
- https://www.typescriptlang.org/docs/handbook/modules/guides/choosing-compiler-options.html (fetched 2026-10-04; nodenext for Node, bundler for bundlers)
