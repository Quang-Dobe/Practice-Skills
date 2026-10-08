# Runtime validation

> Load when: parsing untrusted data (request body, env vars, JSON, config files), schemas, Zod, Valibot, ArkType. Pinned: TypeScript 7.0.2, Node 24 LTS, Zod 4.x (zod.dev lists 4.6 as recent) (2026-10-04).

## Existing repo
- How to recognise it: `zod`, `valibot` or `arktype` in `package.json`; `z.object(` / `v.object(` / `type({` in code. The conventions file records it as `validation:`.
- Rule: keep the library the repo uses; never add a second one. Do not rewrite schemas to Zod unasked.

## New repo default
- Validate at every boundary: env vars, request input, `JSON.parse` output, config files, anything from a file or network. Inside the boundary, trust the types.
- Zod by default (v4). Define the schema once and derive the type with `z.infer`; do not hand-write a parallel interface.
- Use `safeParse` for input you expect to be wrong (returns `{ success, data | error }`); `parse` throws, so it suits startup.
- Env fails fast: parse `process.env` once at startup in one module, let it throw, export the typed result. Env values are strings, so use `z.coerce.number()` for numbers.
- Standard Schema (`StandardSchemaV1`, the `~standard` property with `validate()`) is a shared interface; Zod documents that it implements it, and ArkType 2.1.28+ documents it. Valibot's support was not confirmed on the pages fetched. Code that must accept any library's schema can take a Standard Schema value.
- `z.prettifyError`, `z.treeifyError` and `z.flattenError` format a `ZodError`.

```ts
import { z } from "zod"; // Zod 4.x

const Env = z.object({
  NODE_ENV: z.enum(["development", "test", "production"]).default("development"),
  PORT: z.coerce.number().default(3000),
  DATABASE_URL: z.string().min(1),
});
export type Env = z.infer<typeof Env>;

// Fail fast: throws a ZodError at startup if env is wrong.
export const env: Env = Env.parse(process.env);

const User = z.object({ id: z.string(), name: z.string() });
export type User = z.infer<typeof User>;

export function parseUser(json: string): User {
  const result = User.safeParse(JSON.parse(json));
  if (!result.success) {
    throw new Error(`Invalid user: ${z.prettifyError(result.error)}`, {
      cause: result.error,
    });
  }
  return result.data;
}
```

## Avoid
- `JSON.parse(s) as User` → a cast verifies nothing → `safeParse` the parsed value.
- Reading `process.env.X` all over the code → `undefined` surfaces late → one validated `env` module.
- Hand-written interface next to a schema → the two drift → `z.infer`.
- Validating deep inside business logic → duplicate checks, unclear trust line → validate once at the edge.
- Mixing Zod, Valibot and ArkType in one repo → three APIs and bundles → keep the repo's one library.
- Copying Zod v3 snippets → v4 changed several APIs → check zod.dev for the v4 form.

## Sources
- https://zod.dev (fetched 2026-10-04; Zod 4 stable, 4.6 recent)
- https://zod.dev/basics (fetched 2026-10-04; `z.object`, `safeParse`, `z.infer`)
- https://zod.dev/api (fetched 2026-10-04; `z.coerce.number()`, `z.enum`, `.default()`)
- https://zod.dev/error-formatting (fetched 2026-10-04; `z.prettifyError`, `z.treeifyError`, `z.flattenError`)
- https://zod.dev/library-authors (fetched 2026-10-04; Zod implements Standard Schema)
- https://valibot.dev (fetched 2026-10-04; `object`, `safeParse`, `InferOutput`)
- https://arktype.io (fetched 2026-10-04; `type({...})`, `type.errors`)
- https://arktype.io/docs/ecosystem (fetched 2026-10-04; ArkType 2.1.28+ implements Standard Schema)
- https://standardschema.dev (fetched 2026-10-04; `StandardSchemaV1`, `~standard`, `validate()`; page names no implementing libraries)
