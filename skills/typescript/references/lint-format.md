# Lint and format

> Load when: ESLint, typescript-eslint, Biome, oxlint, Prettier, lint/format config, husky, lefthook, lint-staged, pre-commit hooks. Pinned: TypeScript 7.0.2, Node 24 LTS (2026-10-04).

## Existing repo
- How to recognise it: `eslint.config.{js,mjs,cjs,ts}` (flat config), `.eslintrc*` (legacy), `.prettierrc*` or a `prettier` key, `biome.json` / `biome.jsonc`, `.oxlintrc.json`, `.husky/`, `lefthook.yml`, a `lint-staged` key or `.lintstagedrc*`.
- Rule: keep the tools that are there. Biome repos stay on Biome (lint + format in one tool); oxlint repos stay on oxlint, with Prettier if it is present. Never swap tools or migrate `.eslintrc` to flat config unasked.
- Run the repo's own lint script (`package.json` `scripts`) before and after your change.

## New repo default
- ESLint flat config in `eslint.config.mjs`, with `typescript-eslint` and its type-checked configs, plus Prettier for formatting.
- `eslint-config-prettier/flat` goes last in the config array, so it turns off rules that fight Prettier. Run Prettier as its own command (`prettier --check .`), not as an ESLint rule.
- Type-checked linting uses `projectService: true`.
- TS 7 constraint: typescript-eslint's supported range is `>=4.8.4 <6.1.0`, and TypeScript 7.0 ships no programmatic API (7.1 is expected to). So a TS 7 repo installs the TS 6 API under the name `typescript` and the 7.0 compiler under another name, exactly as the TS 7.0 announcement shows. ESLint and typescript-eslint then import the 6.x API; type-checking runs the 7.0 compiler.
- Check after install: `pnpm ls typescript typescript-eslint` should show 6.x under `typescript`. Confirm which binary runs `tsc` with `pnpm exec tsc --version` (the announcement says the 6 package provides `tsc6`).
- Re-check typescript-eslint's version-support page when upgrading; drop the alias only after it lists 7.1 or newer.

```json
{
  "devDependencies": {
    "typescript": "npm:@typescript/typescript6@^6.0.2",
    "@typescript/native": "npm:typescript@^7.0.2"
  }
}
```

```js
// eslint.config.mjs
import js from "@eslint/js";
import { defineConfig } from "eslint/config";
import tseslint from "typescript-eslint";
import prettier from "eslint-config-prettier/flat";

export default defineConfig({
  files: ["**/*.{ts,mts}"],
  extends: [js.configs.recommended, tseslint.configs.recommendedTypeChecked, prettier],
  languageOptions: { parserOptions: { projectService: true } },
});
```

### Pre-commit hooks
- Husky: `pnpm add -D husky`, then `pnpm exec husky init` (creates `.husky/pre-commit` and the `prepare` script). Put `pnpm exec lint-staged` in the hook.
- lint-staged config, e.g. `"*.{ts,mts}": ["eslint --fix", "prettier --write"]` (match the ESLint `files` scope, so no file reaches ESLint without a config). Tasks for one glob run in order.
- Lefthook alternative: `lefthook.yml` plus `lefthook install`; its docs show `pre-commit` jobs running linters with `stage_fixed: true`.
- Use whichever hook tool the repo already has. Hooks are fast checks only; the full `tsc --noEmit` stays in CI.

## Avoid
- `eslint-plugin-prettier` as the default → slow, noisy diagnostics → Prettier as a separate command.
- Installing TS 7 as plain `typescript` with typescript-eslint → peer range error or a missing API → the alias form above.
- Type-checked rules with `parserOptions.project` globs in new configs → manual maintenance → `projectService: true`.
- Adding Prettier to a Biome repo, or ESLint to an oxlint repo → duplicate formatters/linters → keep the one tool.
- Legacy `.eslintrc` in a new repo → superseded by flat config → `eslint.config.mjs`.

## Sources
- https://typescript-eslint.io/getting-started/ (fetched 2026-10-04; install, flat config, `defineConfig`)
- https://typescript-eslint.io/getting-started/typed-linting (fetched 2026-10-04; `projectService`, `recommendedTypeChecked`)
- https://typescript-eslint.io/users/dependency-versions (fetched 2026-10-04; supported TypeScript `>=4.8.4 <6.1.0`)
- https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/ (fetched 2026-10-04; no API in 7.0, 7.1 API expected, `@typescript/typescript6` alias, `tsc6`)
- https://eslint.org/docs/latest/use/configure/configuration-files (fetched 2026-10-04; config file names)
- https://prettier.io/docs/ (fetched 2026-10-04; the page links to a linter-integration page, not fetched)
- https://github.com/prettier/eslint-config-prettier (fetched 2026-10-04; `eslint-config-prettier/flat`, place last)
- https://biomejs.dev (fetched 2026-10-04; `biome check --write`; the page does not mention type-aware linting)
- https://oxc.rs/docs/guide/usage/linter (fetched 2026-10-04; `pnpm add -D oxlint`; its type-aware mode uses tsgo, TypeScript 7)
- https://typicode.github.io/husky/get-started.html (fetched 2026-10-04; `husky init`)
- https://lefthook.dev (fetched 2026-10-04; `lefthook.yml`, `lefthook install`)
- https://github.com/lint-staged/lint-staged (fetched 2026-10-04; config files, sequential task arrays)
