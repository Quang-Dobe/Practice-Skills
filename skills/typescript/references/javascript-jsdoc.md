# JavaScript with JSDoc

> Load when: plain `.js` files, JSDoc types, `checkJs`, types without converting to TS. Pinned: TypeScript 7.0.2, Node 24 LTS (2026-10-04).

## Existing repo
- How to recognise it: `.js`/`.mjs` sources with `/** @type */` or `@param {…}` comments, `// @ts-check` at file tops, `checkJs`/`allowJs` in `tsconfig.json` or `jsconfig.json`. The conventions file records `language: js-jsdoc`.
- Rule: stay in JavaScript with JSDoc. Do not convert files to `.ts` unasked.

## New repo default
- Turn checking on for the whole project: `"allowJs": true` and `"checkJs": true` in `tsconfig.json`. Per file, use `// @ts-check` at the top (and `// @ts-nocheck` to opt a file out).
- Annotate with `@param {T} name`, `@returns {T}`, `@type {T}`, `@template T`, `@callback`, and `@typedef` for object shapes. Optional parameter: `@param {string} [p]`.
- Import types with `@import` (handbook JSDoc reference lists it) instead of inline `import("./x").T`.
- Ship types to consumers by generating `.d.ts`: `allowJs`, `declaration`, `emitDeclarationOnly`, `outDir`, then point `types` in `package.json` at the output.
- TS 7 notes (release post): `@enum` and `@class` are no longer recognised, the closure function syntax and standalone `?` type are gone, and values need `typeof` where types are expected. The `@import` tag is not listed as removed; this was not tested on a 7.0.2 install.
- Convert to TypeScript when the types need generics-heavy logic, enums, many shared interfaces, or the JSDoc outweighs the code.

```js
// @ts-check
/**
 * @import { Readable } from "node:stream"
 */

/**
 * @typedef {object} User
 * @property {string} id
 * @property {string} name
 * @property {number} [age]
 */

/**
 * @template T
 * @param {T[]} items
 * @param {(item: T) => boolean} pred
 * @returns {T | undefined}
 */
export function findFirst(items, pred) {
  return items.find(pred);
}

/**
 * @param {Readable} input
 * @returns {User}
 */
export function parse(input) {
  return { id: "1", name: String(input) };
}
```

```json
{ "compilerOptions": { "strict": true, "types": ["node"], "allowJs": true, "checkJs": true,
  "declaration": true, "emitDeclarationOnly": true, "outDir": "dist" }, "include": ["src"] }
```

- TS 7 defaults `types` to `[]`, so `node:` imports and Node globals need `"types": ["node"]` plus `pnpm add -D @types/node`.

## Avoid
- JSDoc types left unchecked (no `checkJs`/`@ts-check`) → comments become decoration → turn checking on.
- Hand-writing a `.d.ts` beside JS → drifts from the code → generate it with `emitDeclarationOnly`.
- `@enum`, `@class`, closure-style types → dropped in TS 7 → `@typedef` on `(typeof X)[keyof typeof X]`, real `class`, TS syntax types.
- `@type {Object}` / `{*}` everywhere → effectively `any` → real shapes via `@typedef`.
- Converting a JS repo to TS unasked → large diff nobody requested → ask first.

## Sources
- https://www.typescriptlang.org/docs/handbook/jsdoc-supported-types.html (fetched 2026-10-04; `@import`, `@param`, `@returns`, `@typedef`, `@template`, `@callback`)
- https://www.typescriptlang.org/docs/handbook/type-checking-javascript-files.html (fetched 2026-10-04; `checkJs`, `allowJs`, `// @ts-check`)
- https://www.typescriptlang.org/docs/handbook/declaration-files/dts-from-js.html (fetched 2026-10-04; `.d.ts` generation config)
- https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/ (fetched 2026-10-04; TS 7 JSDoc removals)
- https://github.com/microsoft/typescript-go/blob/main/CHANGES.md (fetched 2026-10-04; JSDoc differences; no `@import` entry)
