# Async patterns

> Load when: `async`/`await`, promises, parallel work, timeouts, retries, cancellation, `AbortController`. Pinned: TypeScript 7.0.2, Node 24 LTS (2026-10-04).

## Existing repo
- How to recognise it: existing helpers (`p-limit`, `p-retry`, own `retry()`/`sleep()`), `no-floating-promises` in the ESLint config, `AbortController` usage.
- Rule: follow what is there. Do not swap a working retry or queue library for the code below.

## New repo default
- Independent work runs in parallel. `Promise.all`: one failure fails the lot (rejects with the first reason). `Promise.allSettled`: you need every outcome (never rejects; gives `{status, value|reason}`). `Promise.any`: first success (rejects with `AggregateError` if all fail). `Promise.race`: first to settle, success or failure.
- Cancel with `AbortController`; take an optional `signal` parameter and pass it to every callee (`fetch`, your own functions).
- `AbortSignal.timeout(ms)` makes a self-aborting signal; `AbortSignal.any([a, b])` aborts when any input does. Both are Stable in Node 24 (`timeout` added v17.3.0, `any` added v20.3.0).
- Retry with a hard attempt limit, never retry once the caller's signal aborted, and rethrow with the last error as `cause`.
- Every promise is awaited, returned, or deliberately `void`-ed. Enable typescript-eslint `no-floating-promises` (needs type information) and `no-misused-promises`.

```ts
export async function fetchJson(
  url: string,
  opts: { signal?: AbortSignal; timeoutMs?: number; attempts?: number } = {},
): Promise<unknown> {
  const { signal, timeoutMs = 5_000, attempts = 3 } = opts;
  let lastError: unknown;
  for (let i = 1; i <= attempts; i++) {
    const timeout = AbortSignal.timeout(timeoutMs);
    const combined = signal ? AbortSignal.any([signal, timeout]) : timeout;
    try {
      const res = await fetch(url, { signal: combined });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (e: unknown) {
      lastError = e;
      if (signal?.aborted) throw e; // caller cancelled: do not retry
    }
  }
  throw new Error(`Failed after ${attempts} attempts`, { cause: lastError });
}

const [a, b] = await Promise.all([fetchJson("/a"), fetchJson("/b")]);
const settled = await Promise.allSettled(ids.map((id) => fetchJson(`/x/${id}`)));
```

## Avoid
- Floating promise (`save();` with no await) → errors vanish as unhandled rejections → `await`, `return`, or `void save()` on purpose.
- `items.forEach(async (x) => { await f(x); })` → forEach ignores the returned promises, so nothing waits and errors escape (`no-misused-promises` flags it) → `for (const x of items) await f(x)` in sequence, or `await Promise.all(items.map(f))` in parallel.
- `await` in a loop over independent work → needless serial latency → `Promise.all`.
- Unbounded retry → hammers a failing service → fixed attempt limit; add backoff if the repo already has a helper.
- Dropping the `signal` between layers → cancellation silently stops working → pass it down every call.

## Sources
- https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise (fetched 2026-10-04; `all`, `allSettled`, `any`, `race` semantics)
- https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal (fetched 2026-10-04; `any()`, `timeout()`; the page has no Node data)
- https://nodejs.org/api/globals.html (fetched 2026-10-04; `AbortSignal.timeout` v17.3.0, `AbortSignal.any` v20.3.0, both Stable, so present in Node 24)
- https://typescript-eslint.io/rules/no-floating-promises/ (fetched 2026-10-04; requires type information; `void` allowed by default)
- https://typescript-eslint.io/rules/no-misused-promises/ (fetched 2026-10-04; `checksVoidReturn` flags async `forEach` callbacks)
