# Hooks and Effects

> Load when: `useEffect`, custom hooks, rules of hooks, hooks in conditions, `use(...)`, Suspense for data, syncing state with props. Pinned: React 19.3, Vite 8, React Compiler 1.0, React Router 8.

## Existing repo
- How to recognise it: `useEffect` and custom `use*` hooks in `src/`; `server-state` in the conventions file (`fetch-in-effects` means effects fetch data).
- Rule: follow what is there. A `fetch-in-effects` repo keeps that style unless asked; use the race-safe pattern below. With a server-state library, fetch through it, not in effects.

## New repo default
- Call hooks only at the top level of components and custom hooks: not in loops, conditions, nested functions, event handlers or `try`/`catch`. `eslint-plugin-react-hooks` enforces it.
- `use` is the one exception: `use(Context)` and `use(promise)` may sit in conditions and loops, but only inside a component or hook, and not in `try`/`catch` (use an error boundary).
- Custom hooks: `use` prefix only when the function calls hooks. They share logic, not state: each call gets its own state.
- Before an effect, ask: derive during render (no effect for computed values), handle user actions in event handlers, reset state with `key` (`<Profile userId={id} key={id} />`).
- Effects only sync with external systems (network, subscriptions, non-React widgets). Return a cleanup; list every reactive value in the dependency array.
- Fetching in an effect (only when no server-state library): guard against races with a cleanup flag or `AbortController`.
- `use(promise)` inside `<Suspense>`: the promise must be cached or created outside render; a new promise each render suspends again.

```tsx
import { useEffect, useState } from 'react';

type User = { id: string; name: string };

// Callers reset on id change with a key: <UserPanel key={userId} userId={userId} />
export function useUser(userId: string) {
  const [user, setUser] = useState<User | null>(null);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    fetch(`/api/users/${userId}`, { signal: controller.signal })
      .then((r) => {
        if (!r.ok) throw new Error(`Request failed: ${r.status}`);
        return r.json() as Promise<User>;
      })
      .then(setUser)
      .catch((e: unknown) => {
        if (!controller.signal.aborted) setError(e as Error);
      });
    return () => controller.abort();
  }, [userId]);

  return { user, error };
}
```

## Avoid
- `useEffect` + `setState` to compute a value → extra render pass → compute it during render.
- Effect for a button click or submit → runs too late to know user intent → event handler.
- Skipping or lying about dependencies → stale values → declare all; restructure instead of suppressing the lint.
- `use(fetch(...))` created in render → new promise every render → cache it or pass it from above.
- `useMount`/`useEffectOnce`-style wrappers → hide missing dependencies → name hooks after their purpose.

## Sources
- https://react.dev/reference/rules/rules-of-hooks (fetched 2026-10-08)
- https://react.dev/learn/reusing-logic-with-custom-hooks (fetched 2026-10-08)
- https://react.dev/learn/you-might-not-need-an-effect (fetched 2026-10-08)
- https://react.dev/learn/synchronizing-with-effects (fetched 2026-10-08)
- https://react.dev/reference/react/use (fetched 2026-10-08)
