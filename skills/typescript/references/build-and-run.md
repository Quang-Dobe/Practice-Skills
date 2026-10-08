# Build and run

> Load when: building, bundling or running TypeScript, `tsx`, type stripping, `tsc`, tsup, tsdown, esbuild, CI type-check, publishing a package. Pinned: TypeScript 7.0.2, Node 24 LTS (2026-10-04).

## Existing repo
- How to recognise it: `package.json` `scripts` (`build`, `dev`, `start`), `tsup.config.*`, `tsdown.config.*`, build scripts calling `esbuild`, `tsx` in scripts or devDependencies, `node --experimental-strip-types` in scripts.
- Rule: keep the repo's builder and runner. Do not swap tsup for tsdown (or the reverse) unasked.
- tsup: its repository states "This project is not actively maintained anymore" and recommends tsdown. Mention it once; do not migrate unasked.

## New repo default
- Run `.ts` directly with Node type stripping (Node 24 LTS: on by default, stable since 24.12). Node only erases types; it does no type-checking and ignores `tsconfig.json`.
- Type stripping limits: no enums, no `namespace` with runtime code, no parameter properties, no import aliases, no decorators; no `.tsx`; no stripping inside `node_modules`. Relative imports are written with the `.ts` extension (`./a.ts`), and type-only imports need `import type`.
- Set `erasableSyntaxOnly: true` and `verbatimModuleSyntax: true` in `tsconfig.json` so `tsc` rejects the syntax Node cannot run (Node's page recommends both). Add `allowImportingTsExtensions` for `noEmit` setups, or `rewriteRelativeImportExtensions` when `tsc` emits JS (it rewrites `./a.ts` to `./a.js`; added in TypeScript 5.7).
- Default stack: Node type stripping to run; `tsc` builds libraries (emits JS + `.d.ts`); tsdown when bundling is needed; `tsx` only when non-erasable syntax (enums, etc.) is unavoidable (`tsx file.ts`; it does not type-check). tsup is not offered for new repos; keep it where it already exists.
- CI: `tsc --noEmit`. Type stripping, tsx, esbuild, tsdown and tsup all drop types without checking them.
- TS 7 repos: put the 7.0 compiler in `@typescript/native` and alias `typescript` to `@typescript/typescript6` for tools that need the API (same form as in the lint reference). Confirm the binary with `pnpm exec tsc --version`.
- Libraries: `tsc` (emits `.js` and `.d.ts`; declaration emit was rewritten for TS 7, see below). Bundling needed: tsdown. App code that must be bundled: esbuild (it also does not emit `.d.ts`).

```json
{
  "type": "module",
  "scripts": {
    "dev": "node --watch src/main.ts",
    "typecheck": "tsc --noEmit",
    "build": "tsdown",
    "test": "vitest run"
  }
}
```

### Declaration files under TS 7
- TS 7.0 has no stable programmatic API (7.1 is expected to add a new one). Tools that call the TS API need the TS 6 package.
- tsdown (via rolldown-plugin-dts): with `isolatedDeclarations` on, it uses oxc-transform (needs no TypeScript package, very fast); otherwise it falls back to the TypeScript compiler. The plugin picks oxc if `isolatedDeclarations` is on, tsgo if TypeScript 7 is installed (marked experimental), else tsc, which needs TypeScript 5.x or 6.x. Safest on TS 7: turn on `isolatedDeclarations`.
- rollup-plugin-dts says TS 7 has no compiler API and tells you to install `@typescript/typescript6`; it falls back to that package.
- tsup: I could not verify how its `dts` option works or whether it supports TS 7; its docs page returned no content. Flagged unverified; do not promise it works with TS 7.
- esbuild: never emits `.d.ts`.
- `tsc` itself: yes, TS 7 emits `.d.ts` files. The typescript-go changelog says declaration emit was "fundamentally rewritten", and the 7.0 announcement names only the programmatic API as missing. Output need not match TS 6 byte for byte, and declaration emit is not well-defined when the program has errors. Run `tsc --declaration --emitDeclarationOnly` and diff or inspect the result when upgrading.

### Publishing a library
- `exports` in `package.json` is the entry map (it overrides `main`; unlisted subpaths throw `ERR_PACKAGE_PATH_NOT_EXPORTED`). Put `"types"` first in each condition block, then `import`, `require`, `default`.
- Ship `.d.ts` files that match each output format.
- Check the packed tarball with `pnpm pack`, then `attw --pack` (`@arethetypeswrong/cli`; the web tool takes a package name or `npm pack` output).

```json
{
  "exports": {
    ".": { "types": "./dist/index.d.ts", "import": "./dist/index.js" }
  },
  "files": ["dist"]
}
```

## Avoid
- Enums, namespaces or constructor parameter properties under type stripping → Node errors → `as const` objects, plain classes, or `tsx`.
- Assuming a build passing means types pass → bundlers skip checks → `tsc --noEmit` in CI.
- `main` only for a new library → no subpath control → `exports`.
- Putting `"types"` after `import` or `require` → TypeScript may not reach it → `types` first.
- Pairing tsup `dts` with TS 7 unchecked → possible missing-API failure → run the build and `attw --pack` first.

## Sources
- https://nodejs.org/api/typescript.html (fetched 2026-10-04; stable in 24.12, limits, recommended tsconfig)
- https://tsx.is (the fetch failed with a certificate error; https://tsx.hirok.io was fetched 2026-10-04; `tsx file.ts`, `tsx watch`)
- https://tsdown.dev (fetched 2026-10-04; Rolldown and Oxc based; also https://tsdown.dev/options/dts fetched 2026-10-04)
- https://github.com/sxzz/rolldown-plugin-dts (fetched 2026-10-04; oxc, tsc and tsgo generators)
- https://github.com/Swatinem/rollup-plugin-dts (fetched 2026-10-04; needs `@typescript/typescript6` on TS 7)
- https://tsup.egoist.dev (fetched 2026-10-04; no content); https://github.com/egoist/tsup (fetched 2026-10-04; maintenance notice)
- https://esbuild.github.io (fetched 2026-10-04); https://esbuild.github.io/content-types/#typescript (fetched 2026-10-04; no type-check, no `.d.ts`)
- https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/ (fetched 2026-10-04; no API in 7.0, alias form, mentions separate syntactic declaration emit)
- https://github.com/microsoft/typescript-go/blob/main/CHANGES.md (fetched 2026-10-04; declaration emit rewritten, not byte-identical to TS 6)
- https://www.typescriptlang.org/tsconfig/ (fetched 2026-10-04; `allowImportingTsExtensions` since 5.0, `rewriteRelativeImportExtensions` since 5.7)
- https://nodejs.org/api/packages.html#package-entry-points (fetched 2026-10-04; `exports`, `types` condition)
- https://arethetypeswrong.github.io (fetched 2026-10-04; `attw --pack`)
