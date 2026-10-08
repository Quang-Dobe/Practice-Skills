# Project structure

> Load when: scaffolding a new project or package, adding a module or folder, moving files, choosing a folder layout, or touching `index.ts` barrel files. Pinned: TypeScript 7.0.2, Node 24 LTS (2026-10-04).

## Existing repo
- How to recognise it: feature layout = top-level folders named after domain concepts (`src/billing/`, `src/users/`). Layer layout = folders named after technical roles (`src/controllers/`, `src/services/`, `src/models/`). Check `layout:` in the conventions file first.
- Rule: follow what is there. Put new files where the nearest sibling files live. Never reorganise folders or add or remove barrels unasked.
- Keep the repo's test location (colocated or a `test/` tree) and its barrel habits.

## New repo default
- Feature folders: one folder per domain concept, holding everything that changes together.
- One public `index.ts` per package is fine: it is the package entry and what `exports` in `package.json` points at. Everything else imports by file path.
- No deep barrels: an `index.ts` that re-exports a folder inside a package. They create import cycles and make bundlers and test runners load unused modules. Vite's performance guide recommends importing the specific file instead of an index.
- Colocate tests: `thing.ts` next to `thing.test.ts`.
- Write the `.ts` extension in relative imports (`./thing.ts`), with `allowImportingTsExtensions` (type-check or `noEmit` setups) or `rewriteRelativeImportExtensions` (when `tsc` emits JS). Vite's guide says explicit extensions save resolution checks, and Node requires them for ESM. An existing repo keeps its own convention.
- Private cross-folder aliases: `package.json` `"imports"` with `#` keys pointing at `.ts` files. Node resolves them natively.

Feature layout:

```text
src/
  index.ts            # the package's one public barrel
  billing/
    invoice.ts
    invoice.test.ts
    pricing.ts
  users/
    user.ts
    user.test.ts
  shared/
    result.ts
```

Layer layout, when the repo already uses it:

```text
src/
  controllers/  services/  models/  utils/
```

## Avoid
- `index.ts` in every folder re-exporting siblings → cycles, slow bundling and test start-up → import the file directly.
- `export *` from the package barrel for internal helpers → leaks private API → export named public symbols only.
- Mixing both layouts in one package → nobody knows where a file goes → pick the one the repo has.
- A `utils/` or `common/` dump → grows without owner → name the folder after what it does.
- Moving files in an existing repo to match the default → large unasked diff → leave it.

## Sources
- https://vite.dev/guide/performance.html (fetched 2026-10-04; avoid barrel files, explicit extensions)
- https://nodejs.org/api/packages.html (fetched 2026-10-04; `exports` entry points, `imports` with `#` keys, encapsulation)
