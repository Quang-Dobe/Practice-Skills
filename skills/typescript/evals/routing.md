# TypeScript routing evals

Each prompt assumes the `typescript` skill is loaded. Pass = agent opens every `expect` file, none of the `must-not` files, and shows `behavior` when given. Unless the prompt describes the repo's state (e.g. empty folder, no conventions file), assume the repo already has .claude/conventions/typescript.md.

## E01
prompt: Start a new TypeScript CLI tool in this empty folder.
expect: choose-conventions.md, project-structure.md, tsconfig.md
must-not: detect-conventions.md

## E02
prompt: Repo has package.json and tsconfig.json but no .claude/conventions/typescript.md. Rename getUser to fetchUser across src/.
expect: detect-conventions.md, ts-style.md
must-not: choose-conventions.md

## E03
prompt: Review this function for style issues: `export default function(x: any) { var r = x.items.map(i => i.v); return r }`
expect: ts-style.md
must-not: build-and-run.md, packages-and-monorepo.md

## E04
prompt: Imports fail with ERR_REQUIRE_ESM after I set "type": "module" in package.json.
expect: tsconfig.md
must-not: testing.md

## E05
prompt: Model a payment status that is pending, paid with a receiptId, or failed with a reason, and make every switch over it exhaustive.
expect: type-patterns.md
must-not: runtime-validation.md

## E06
prompt: Fetch three URLs in parallel and cancel all of them if any takes longer than 5 seconds.
expect: async.md
must-not: testing.md

## E07
prompt: Our functions throw plain strings; set up one consistent error-handling approach.
expect: error-handling.md
must-not: testing.md

## E08
prompt: Validate environment variables at startup and fail fast if DATABASE_URL is missing.
expect: runtime-validation.md
must-not: testing.md

## E09
prompt: Add type checking to our plain JavaScript utils without converting them to TypeScript.
expect: javascript-jsdoc.md
must-not: build-and-run.md

## E10
prompt: Where should a new billing module live, and should it have an index.ts?
expect: project-structure.md
must-not: testing.md

## E11
prompt: Add lodash-es as a dependency of the api package in our pnpm workspace.
expect: packages-and-monorepo.md
must-not: testing.md

## E12
prompt: Move our lint setup to ESLint flat config and run it on staged files before each commit.
expect: lint-format.md
must-not: testing.md

## E13
prompt: Write unit tests for parseDuration() with Vitest.
expect: testing.md
must-not: build-and-run.md

## E14
prompt: Bundle the library for npm with type declarations, and make CI fail on type errors.
expect: build-and-run.md
must-not: testing.md

## E15
prompt: Build a React component for the login form.
expect: none
must-not: project-structure.md, ts-style.md
behavior: says React/UI components are out of scope for this skill

## E16
prompt: Add an Express route POST /orders with auth middleware.
expect: none
must-not: project-structure.md, ts-style.md
behavior: says Node back-end frameworks are out of scope for this skill

## E17
prompt: Explain the difference between git merge and git rebase.
expect: none
must-not: ts-style.md

## E18
prompt: .claude/conventions/typescript.md says "test: vitest", but the package I'm editing has jest.config.js and Jest tests. Add a test for formatDate.
expect: none
must-not: detect-conventions.md, choose-conventions.md
behavior: flags the mismatch and asks which wins before writing code

## E19
prompt: .claude/conventions/typescript.md lists "lint-format: biome". Add a rule that bans console.log.
expect: lint-format.md
must-not: detect-conventions.md
behavior: configures Biome; does not propose migrating to ESLint

## E20
prompt: Repo root has apps/web (React) and packages/core (package.json + tsconfig.json), no conventions file. Add a slugify() helper to packages/core.
expect: detect-conventions.md, ts-style.md
must-not: choose-conventions.md
behavior: scopes the convention scan to packages/core and the repo root, not apps/web

## E21
prompt: .claude/conventions/typescript.md exists. Add loadConfig() that reads config.json, validates it with Zod, and retries the read once with a 2-second timeout.
expect: runtime-validation.md, async.md
must-not: testing.md
