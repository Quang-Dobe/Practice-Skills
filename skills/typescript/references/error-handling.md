# Error handling

> Load when: `try`/`catch`, custom errors, error flow, Result types, neverthrow. Pinned: TypeScript 7.0.2, Node 24 LTS (2026-10-04).

## Existing repo
- How to recognise it: `neverthrow` (or another Result library) in `package.json` plus `Result`/`ok(`/`err(` in code means result style; `throw` plus custom `class ...Error` means exceptions. The conventions file records it as `error-style:`.
- Rule: follow what is there. Never mix the two styles inside one module; convert at the module edge (wrap a throwing call, or unwrap a result).

## New repo default
- Exceptions for unexpected failures. Throw `Error` subclasses, never strings or plain objects (they carry no stack).
- Wrap and rethrow with `cause` (`new Error(msg, { cause: e })`) so the original stack survives; `cause` may be any value, including structured data.
- `catch (e: unknown)`: `useUnknownInCatchVariables` is on under `strict` (since TS 4.4). Narrow with `instanceof` before reading `message`.
- Give domain errors a `name` and the fields callers need; match them with `instanceof`.
- Result types (neverthrow: `ok`, `err`, `Result`, `ResultAsync`, `andThen`, `match`) only when the repo already uses them or the user asks.
- Catch only where you can act (retry, translate, report); otherwise let it propagate.

```ts
export class NotFoundError extends Error {
  override name = "NotFoundError";
  readonly resource: string;
  constructor(resource: string, options?: ErrorOptions) {
    super(`${resource} not found`, options);
    this.resource = resource;
  }
}

export async function loadConfig(path: string): Promise<string> {
  try {
    return await readText(path);
  } catch (e: unknown) {
    if (e instanceof Error && "code" in e && e.code === "ENOENT") {
      throw new NotFoundError(path, { cause: e });
    }
    throw new Error(`Cannot read config ${path}`, { cause: e });
  }
}

try {
  await loadConfig("app.json");
} catch (e: unknown) {
  if (e instanceof NotFoundError) console.warn(e.resource);
  else throw e;
}
```

## Avoid
- `throw "oops"` → no stack, not an `Error` → `throw new Error("oops")`.
- `catch (e) { log(e.message) }` → `e` may not be an Error → `catch (e: unknown)` plus `instanceof`.
- Rethrowing a new error without `cause` → original stack lost → `{ cause: e }`.
- Empty `catch {}` → hides failures → handle, or rethrow.
- `Result` returns and `throw` in one module → callers cannot know which to handle → pick one per module.
- Constructor parameter properties (`constructor(readonly x: string)`), enums and namespaces → not erasable syntax, so Node type stripping and `erasableSyntaxOnly` reject them → declare the field in the class body and assign it in the constructor.
- Adding neverthrow to an exceptions repo unasked → migration nobody requested → keep exceptions.

## Sources
- https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Error/cause (fetched 2026-10-04; `{ cause }` option, any value)
- https://www.typescriptlang.org/tsconfig/#useUnknownInCatchVariables (fetched 2026-10-04; default true under `strict`, TS 4.4)
- https://nodejs.org/api/typescript.html (fetched 2026-10-04; type stripping does not support parameter properties, enums, runtime namespaces)
- https://github.com/supermacro/neverthrow (fetched 2026-10-04; `Result`, `ResultAsync`, `andThen`, `match`, `safeTry`, `eslint-plugin-neverthrow`)
