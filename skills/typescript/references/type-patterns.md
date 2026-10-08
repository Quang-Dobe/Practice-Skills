# Type patterns

> Load when: designing types or interfaces, unions, generics, `any`/`unknown`, narrowing, type errors. Pinned: TypeScript 7.0.2, Node 24 LTS (2026-10-04).

## Existing repo
- How to recognise it: existing type style in `src/` (`interface` vs `type`, enums, branded IDs), `strict` flags in `tsconfig.json`, typescript-eslint rules (`no-explicit-any`, `no-non-null-assertion`, `consistent-type-assertions`).
- Rule: follow what is there, including its enums or `any` escape hatches. Do not tighten types across a whole codebase unasked; apply the patterns below to new and touched code.

## New repo default
- Model variants as a discriminated union with a literal `kind` field; end every `switch` with an `assertNever` default so a new variant becomes a compile error.
- `satisfies` checks a value against a type without widening it (typos caught, literal types kept). Use it for config tables and lookup maps.
- Brand IDs so a `UserId` cannot be passed as an `OrderId`; create them only in one parsing function.
- Constrain generics (`<T extends { id: string }>`) so the body can use what it needs; do not add a type parameter that appears once.
- Reach for built-ins first: `Pick`, `Omit`, `Partial`, `Readonly`, `ReturnType`, `Awaited`.
- Take external data as `unknown`, then narrow with `typeof`/`in`/`instanceof`, a type predicate (`x is T`) or an assertion function (`asserts x is T`).

```ts
type Shape =
  | { kind: "circle"; radius: number }
  | { kind: "square"; side: number };

export function assertNever(x: never): never {
  throw new Error(`Unhandled variant: ${JSON.stringify(x)}`);
}

export function area(s: Shape): number {
  switch (s.kind) {
    case "circle": return Math.PI * s.radius ** 2;
    case "square": return s.side ** 2;
    default: return assertNever(s);
  }
}

const limits = { free: 10, pro: 100 } satisfies Record<"free" | "pro", number>;

type Brand<T, B extends string> = T & { readonly __brand: B };
export type UserId = Brand<string, "UserId">;
export const toUserId = (s: string): UserId => s as UserId; // the one allowed cast

export function isCircle(v: unknown): v is Extract<Shape, { kind: "circle" }> {
  return typeof v === "object" && v !== null && "kind" in v && v.kind === "circle"
    && "radius" in v && typeof v.radius === "number";
}
export function assertDefined<T>(v: T): asserts v is NonNullable<T> {
  if (v == null) throw new Error("Expected a value");
}
```

## Avoid
- `any` → turns the checker off and spreads → `unknown` plus narrowing, or a generic.
- Unchecked `as` (`JSON.parse(s) as User`) → asserts, does not verify → validate at the boundary (see the runtime-validation reference).
- Non-null `!` → crashes at runtime where the type said safe → narrow, or `assertDefined`.
- `switch` on a union without an exhaustive default → new variants slip through → `assertNever`.
- Type annotation where `satisfies` fits → widens literals, loses autocomplete → `satisfies`.
- Sloppy type guards (returning true for any object) → the compiler trusts your lie → check every field, or use a schema.

## Sources
- https://www.typescriptlang.org/docs/handbook/2/narrowing.html (fetched 2026-10-04; discriminated unions, `never` exhaustiveness, type predicates)
- https://www.typescriptlang.org/docs/handbook/utility-types.html (fetched 2026-10-04; `Pick`, `Omit`, `Partial`, `Readonly`, `ReturnType`, `Awaited`)
- https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html (fetched 2026-10-04; `satisfies`)
- https://www.typescriptlang.org/docs/handbook/release-notes/typescript-3-7.html (fetched 2026-10-04; assertion functions, cited because the narrowing page does not cover `asserts`)
- Branded types: no handbook page fetched; the pattern is an intersection with a phantom property, as shown above.
