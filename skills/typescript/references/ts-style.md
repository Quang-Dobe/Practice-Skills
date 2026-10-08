# TypeScript style

> Load when: writing or reviewing any TS/JS code. Pinned: TypeScript 7.0.2, Node 24 LTS (2026-10-04).

## Existing repo
- How to recognise it: `naming:` in the conventions file, lint config (`eslint.config.*`, `biome.json`), `.prettierrc*`, and the surrounding code.
- Rule: follow what is there, including deviations (default exports, enums, classes). Apply the defaults below only to new code in a repo that has no stated preference.

## New repo default
- Naming: `camelCase` for values, functions, parameters; `PascalCase` for types, interfaces, classes; `UPPER_SNAKE` only for true constants (module-level, never reassigned); kebab-case file names (`user-service.ts`). Google's guide names identifiers the same way (`lowerCamelCase`, `UpperCamelCase`, `CONSTANT_CASE`) but uses `snake_case` files, so kebab-case is this skill's choice.
- Named exports only; no default exports (Google: "Do not use default exports").
- `const` by default, `let` only when reassigned, never `var`.
- Plain functions and modules; use a class only when you need state plus behaviour together.
- Union literals or `as const` objects instead of `enum`. The TS handbook presents `as const` objects as the alternative that stays aligned with JavaScript, and Node type stripping rejects enums. Turn on `erasableSyntaxOnly` in tsconfig to enforce it.
- Immutability: `readonly` properties, `readonly T[]` / `ReadonlyArray`, `as const` for literals; copy instead of mutating.
- `@ts-expect-error` with a reason, never `@ts-ignore` (`@ts-expect-error` fails once the error disappears, so it cannot go stale).

```ts
export const LOG_LEVELS = ["debug", "info", "error"] as const;
export type LogLevel = (typeof LOG_LEVELS)[number];

export interface Config {
  readonly level: LogLevel;
  readonly tags: readonly string[];
}

export function parseLevel(input: string): LogLevel {
  const found = LOG_LEVELS.find((level) => level === input);
  if (found === undefined) throw new Error(`Unknown level: ${input}`);
  return found;
}

// @ts-expect-error legacy API returns number, fixed upstream
const legacy: string = oldApi();
```

- Lint rules that enforce this exist in typescript-eslint: `ban-ts-comment`, `no-explicit-any`, `prefer-as-const`, `no-namespace`, `naming-convention`, `consistent-type-imports`. Enable them only in repos that use typescript-eslint.

## Avoid
- `enum` / `const enum` / runtime `namespace` → not erasable, so Node type stripping rejects them; `const enum` also conflicts with `isolatedModules` → union literals or `as const` objects.
- Default exports → inconsistent import names across files → named exports.
- `var` → function scope bugs → `const` / `let`.
- Classes holding no state → needless ceremony → a module of functions.
- `@ts-ignore` → silences future errors too → `@ts-expect-error` plus a reason.
- Restyling code in a repo with other conventions → noisy diffs → match the file.

## Sources
- https://google.github.io/styleguide/tsguide.html (fetched 2026-10-04; naming, named exports, const, readonly, `@ts-ignore` guidance)
- https://www.typescriptlang.org/docs/handbook/enums.html (fetched 2026-10-04; `as const` object alternative, const enum caveats)
- https://typescript-eslint.io/rules/ (fetched 2026-10-04; rule names listed above exist)
- https://nodejs.org/api/typescript.html (fetched 2026-10-04; enums and runtime namespaces unsupported by type stripping; `erasableSyntaxOnly`)
- https://www.typescriptlang.org/tsconfig/ (fetched 2026-10-04; `erasableSyntaxOnly` option)
