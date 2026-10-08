# Testing

> Load when: writing or running tests, Vitest, Jest, `node:test`, mocks. Pinned: TypeScript 7.0.2, Node 24 LTS (2026-10-04).

## Existing repo
- How to recognise it: `vitest` or `jest` in `package.json` devDependencies; `vitest.config.*` or `vite.config.*` with a `test` key; `jest.config.*` or a `jest` key; test files that import `node:test`.
- Rule: use the framework already there, and match the existing file naming and location. Do not convert Jest to Vitest unasked.
- Jest + ESM: Jest's ESM support is documented as experimental. It needs `node --experimental-vm-modules` (or `NODE_OPTIONS`), `transform: {}` or an ESM-emitting transformer, and `jest.unstable_mockModule()` instead of `jest.mock()` (its factory is required, and the module must be loaded with `await import()` after mocking). `jest` is not a global in ESM: import it from `@jest/globals`.
- Jest + TypeScript: Babel with `@babel/preset-typescript` (no type-check) or `ts-jest`. ts-jest drives the TypeScript API, so with TS 7 it is likely to hit the same missing-API limit as typescript-eslint. I did not verify this; check its docs before pairing it with TS 7.

## New repo default
- Vitest. The getting-started page shows version 5.0.3, requiring Vite 6.4 or newer and Node 22.12 or newer; Node 24 LTS qualifies. It runs TypeScript and ESM through Vite, so no extra transform config is needed.
- Test files are named `*.test.ts` or `*.spec.ts` (Vitest matches on `.test.` or `.spec.` in the name), colocated with the source.
- Import the API explicitly: `import { describe, it, expect, vi } from "vitest"`.
- Run `vitest run` in CI (a single pass); plain `vitest` is watch mode.
- Vitest does not type-check. `tsc --noEmit` stays in CI.
- Test behaviour, not implementation: assert on outputs and observable effects, not on private calls or call order.
- Mock only boundaries (network, clock, filesystem, randomness). Prefer a real in-memory fake over a deep mock of your own modules.
- Zero-dependency packages may use `node:test` with `node:assert` and run `node --test`. It is stable and has `describe`/`it`, hooks, `mock.fn`, and coverage via `--experimental-test-coverage`.

```ts
import { describe, it, expect, vi } from "vitest";
import { sendInvoice } from "./invoice.ts";

describe("sendInvoice", () => {
  it("sends once and returns the id", async () => {
    const send = vi.fn().mockResolvedValue({ id: "m1" });

    const result = await sendInvoice({ total: 120 }, { send });

    expect(result).toEqual({ messageId: "m1" });
    expect(send).toHaveBeenCalledTimes(1);
  });
});
```

## Avoid
- Mocking your own internal modules with `vi.mock` → tests pin the file layout → inject the dependency as an argument.
- Asserting private calls or call order → breaks on refactors → assert results.
- Snapshot tests for large objects → nobody reviews the diffs → explicit `expect` on the fields that matter.
- Real timers and network in unit tests → flaky → `vi.useFakeTimers()` and boundary fakes.
- `jest.mock()` in Jest ESM mode → hoisting does not work in ESM → `jest.unstable_mockModule()`.

## Sources
- https://vitest.dev/guide/ (fetched 2026-10-04; version 5.0.3, requirements, `vitest run`, file naming)
- https://jestjs.io/docs/getting-started (fetched 2026-10-04; Babel and ts-jest TypeScript setup, `@jest/globals`)
- https://jestjs.io/docs/ecmascript-modules (fetched 2026-10-04; experimental ESM, `unstable_mockModule`)
- https://nodejs.org/api/test.html (fetched 2026-10-04; stable runner, `mock.fn`, `node --test`, coverage flag)
