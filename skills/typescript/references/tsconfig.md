# tsconfig and modules

> Load when: `tsconfig.json`, compiler options, ESM vs CommonJS, `import`/`require` errors, `"type": "module"`, `moduleResolution`, path aliases. Pinned: TypeScript 7.0.2, Node 24 LTS (2026-10-04).

## Existing repo
- How to recognise it: `tsconfig*.json` (check `extends`), `package.json` `"type"`, `imports`, `exports`, and file extensions `.mts` / `.cts`.
- Rule: follow what is there. Do not flip `strict`, `module`, `moduleResolution` or `"type"` to fix a one-file problem; tell the user which option causes it.

## New repo default
- Strict baseline: `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `verbatimModuleSyntax`, `isolatedModules`, `skipLibCheck`. The 7.0 announcement says `strict` is on by default in 7.0 (also `module: esnext`, `types: []`); keep it explicit so older tools agree.
- Code Node runs directly: `module: nodenext` (implies `moduleResolution: nodenext`), `"type": "module"` in `package.json`, relative imports written as `./a.ts`, paired with `allowImportingTsExtensions` (with `noEmit` or type-check only) or `rewriteRelativeImportExtensions` (when `tsc` emits JS; it rewrites to `./a.js`). Do not set both in the example below when emitting; `rewriteRelativeImportExtensions` already implies the first. An existing repo keeps its own convention.
- Bundled code: `module: esnext` + `moduleResolution: bundler`, `noEmit: true`. The handbook advises not setting `"type": "module"` or using `.mts` there.
- Running `.ts` with Node type stripping: also `erasableSyntaxOnly: true` and `verbatimModuleSyntax: true`; Node does not read tsconfig.
- Path aliases: use `package.json` `"imports"` with `#` keys (`"#utils/*": "./src/utils/*.ts"`), which Node and TypeScript both resolve. `paths` only informs the type checker and does not rewrite emitted imports.
- Global types: TS 7.0 defaults `types` to `[]`, so nothing under `@types/*` loads automatically. Run `pnpm add -D @types/node` and list `"types": ["node"]` or `process`, `Buffer` and `node:` imports fail to compile.
- CI: `tsc --noEmit`.

```json
{
  "compilerOptions": {
    "target": "esnext",
    "module": "nodenext",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "verbatimModuleSyntax": true,
    "isolatedModules": true,
    "skipLibCheck": true,
    "erasableSyntaxOnly": true,
    "allowImportingTsExtensions": true,
    "types": ["node"],
    "noEmit": true
  },
  "include": ["src"]
}
```

- ESM vs CJS rules: `.mjs`/`.mts` are always ESM, `.cjs`/`.cts` always CommonJS, and `.js`/`.ts` follow the nearest `package.json` `"type"` (`module` = ESM, `commonjs` or absent = CJS).
- `ERR_REQUIRE_ESM`: thrown when `require()` hits an ES module (an ESM-only dependency, or your own `"type": "module"` file loaded from CJS). Fix: convert the caller to ESM, or use `await import()`. Node's packages page says `require()` of an ES module works only when it and its dependencies have no top-level `await` (otherwise `ERR_REQUIRE_ASYNC_MODULE`), so on current Node check that case first.

## Avoid
- `moduleResolution: node` / `node10` → removed in TS 7.0 and blind to `exports`/`imports` → `nodenext` or `bundler`.
- `baseUrl` → removed in 7.0 → `paths` relative to the config, or `imports`.
- `paths` aliases in code Node runs → emit keeps the alias and Node throws → `imports` field.
- Extensionless relative imports under `nodenext` → Node cannot resolve them → write the `.ts` extension.
- `"type": "module"` in a bundler-resolved project without checking the bundler → interop TS cannot analyse → follow the handbook.
- Turning off `strict` to silence errors → hides bugs → fix the types.

## Sources
- https://www.typescriptlang.org/tsconfig/ (fetched 2026-10-04; option descriptions, `paths` does not change emit; `allowImportingTsExtensions` needs `noEmit` or `emitDeclarationOnly`, `rewriteRelativeImportExtensions` since 5.7)
- https://www.typescriptlang.org/docs/handbook/modules/theory.html (fetched 2026-10-04; specifiers not rewritten, format detection)
- https://www.typescriptlang.org/docs/handbook/modules/reference.html (fetched 2026-10-04; `paths` vs `imports`, nodenext vs bundler)
- https://www.typescriptlang.org/docs/handbook/modules/guides/choosing-compiler-options.html (fetched 2026-10-04)
- https://nodejs.org/api/packages.html (fetched 2026-10-04; `type`, `imports` `#` keys, require of ESM)
- https://nodejs.org/api/errors.html (fetched 2026-10-04; `ERR_REQUIRE_ESM`, `ERR_REQUIRE_ASYNC_MODULE`)
- https://nodejs.org/api/typescript.html (fetched 2026-10-04; type stripping settings)
- https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/ (fetched 2026-10-04; 7.0 defaults and removals)
