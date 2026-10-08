# Packages and monorepos

> Load when: installing or adding dependencies, lockfiles, pnpm/npm/yarn/bun, workspaces, Turborepo, Nx. Pinned: TypeScript 7.0.2, Node 24 LTS (2026-10-04).

## Existing repo
- How to recognise the manager from the lockfile: `pnpm-lock.yaml` = pnpm, `package-lock.json` = npm, `yarn.lock` = yarn, `bun.lock` or `bun.lockb` = bun. Also check the `packageManager` field in the root `package.json`.
- Workspaces: `pnpm-workspace.yaml` (pnpm) or a `workspaces` array in the root `package.json` (npm, and others). Task runners: `turbo.json` = Turborepo, `nx.json` = Nx.
- Rule: use the manager the lockfile shows. Never mix managers: no `npm install` in a pnpm repo, and never create a second lockfile. If two lockfiles exist, stop and ask which is real.
- Do not add Turborepo or Nx to a repo that has neither.

## New repo default
- pnpm. Declare it in `package.json` as `"packageManager": "pnpm@<version>"`.
- Corepack: the Corepack readme says it ships with Node.js from 14.19.0 up to but not including 25.0.0. So on Node 25 and later it is not bundled; install it with `npm install -g corepack`, then run `corepack enable`. Node 24 LTS still bundles it. Do not assume `corepack` exists on a machine; check `corepack --version`.
- Workspace: `pnpm-workspace.yaml` at the repo root listing package globs.
- Internal dependencies use the `workspace:` protocol. pnpm resolves only to local packages and, on pack or publish, rewrites e.g. `workspace:^1.5.0` to `^1.5.0`.
- Add a dependency to one package with `--filter`; add to the workspace root with `-w`.
- Turborepo or Nx only when many packages make task caching worth it (repeated build/test/lint across packages, CI time). Turborepo is a `turbo.json` over existing scripts; Nx adds a project graph, caching and boundary rules.

```yaml
# pnpm-workspace.yaml
packages:
  - "packages/*"
  - "apps/*"
```

```bash
pnpm --filter @acme/api add zod          # one package
pnpm --filter @acme/api add @acme/core   # local pkg, saved as workspace: range
pnpm -w add -D eslint                    # workspace root
pnpm --filter "...@acme/core" test       # core plus its dependents
```

## Avoid
- Mixed lockfiles → drift between installs → one manager, delete the stray lockfile only after asking.
- Hand-editing the lockfile → corrupt resolution → run the manager's command.
- `npm install` inside a workspace package with pnpm → bypasses the workspace → use `pnpm --filter`.
- Hard-coding `"@acme/core": "1.2.3"` for a local package → pulls the registry copy → `workspace:`.
- Adding Turborepo or Nx to a three-package repo → config cost without a cache payoff → plain `pnpm -r` scripts.

## Sources
- https://pnpm.io/workspaces (fetched 2026-10-04; `pnpm-workspace.yaml`, `workspace:` protocol, `-w`)
- https://pnpm.io/filtering (fetched 2026-10-04; `--filter` selectors)
- https://docs.npmjs.com/cli/using-npm/workspaces (the URL returned no usable body; the v11 page https://docs.npmjs.com/cli/v11/using-npm/workspaces was fetched 2026-10-04; `workspaces`, `-w`, `--workspaces`)
- https://nodejs.org/api/corepack.html (fetched 2026-10-04; redirects to https://github.com/nodejs/corepack#readme, fetched 2026-10-04; distributed before 25.0.0, install and enable commands, `packageManager`)
- https://turborepo.com/docs (fetched 2026-10-04; redirects to https://turborepo.dev/docs; caching, `turbo.json`)
- https://nx.dev/getting-started/intro (fetched 2026-10-04; caching, project graph)
