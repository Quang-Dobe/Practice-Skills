# Server state

> Load when: fetching API data, caching, refetching, mutations, loading/error states for data, TanStack Query, SWR, RTK Query. Pinned: React 19.3, Vite 8, React Compiler 1.0, React Router 8.

## Existing repo
- How to recognise it: `@tanstack/react-query` (`useQuery`, `QueryClientProvider`), `swr` (`useSWR`), `@reduxjs/toolkit` with `createApi`, or `fetch`/`axios` inside `useEffect` (conventions file: `server-state: fetch-in-effects`).
- Rule: follow what is there. Keep SWR and RTK Query. A repo that fetches in effects keeps that style unless the user asks to change it; do not add TanStack Query to it unasked.
- Never mirror fetched data into `useState` or a global store, whichever tool the repo uses.
- Suspense mode only if the repo already uses it.

## New repo default
- TanStack Query (`@tanstack/react-query`): one `QueryClient`, wrapped around the app in `QueryClientProvider`.
- `useQuery` with an array `queryKey` that includes every variable the `queryFn` uses; array order matters, object key order does not.
- One query-key factory per feature (for example `src/features/<name>/keys.ts`) so keys and invalidations stay consistent.
- Writes: `useMutation`, then `invalidateQueries` in `onSuccess`; return the promise so the mutation stays pending until the refetch finishes.
- Set `staleTime` deliberately instead of leaving every query to refetch as soon as it is stale.
- Render `isPending`, `error` and data states explicitly; `fetch` does not reject on HTTP errors, so the `queryFn` must throw on a non-OK response (`fetchJson` below).

```tsx
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

type Todo = { id: string; title: string };
async function fetchJson<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, init);
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json() as Promise<T>;
}

export const todoKeys = {
  all: ['todos'] as const,
  list: (status: string) => [...todoKeys.all, 'list', status] as const,
};

export function Todos({ status }: { status: string }) {
  const queryClient = useQueryClient();
  const { isPending, error, data } = useQuery({
    queryKey: todoKeys.list(status),
    queryFn: () => fetchJson<Todo[]>(`/api/todos?status=${status}`),
    staleTime: 30_000,
  });
  const add = useMutation({
    mutationFn: (title: string) =>
      fetchJson<Todo>('/api/todos', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ title }) }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: todoKeys.all }),
  });
  if (isPending) return <p role="status">Loading...</p>;
  if (error) return <p role="alert">{error.message}</p>;
  return <button onClick={() => add.mutate('New')}>Add ({data.length})</button>;
}
```

## Avoid
- `useQuery` data copied into `useState` or a store → stale duplicate that never refetches → use `data` directly.
- Keys missing a variable the `queryFn` reads → wrong cache hits → put every variable in the key.
- Hand-typed key arrays scattered around → invalidation misses → a key factory.
- New code fetching in `useEffect` (outside a repo that already does) → no cache, races, manual loading state → TanStack Query.
- Adding a second server-state library to a repo that has one → two caches → keep the existing one.

## Sources
- https://tanstack.com/query/latest/docs/framework/react/overview (fetched 2026-10-08)
- https://tanstack.com/query/latest/docs/framework/react/guides/query-keys (fetched 2026-10-08)
- https://tanstack.com/query/latest/docs/framework/react/guides/invalidations-from-mutations (fetched 2026-10-08)
- https://swr.vercel.app (redirects to https://vercel.com/oss/swr, fetched 2026-10-08)
- https://redux-toolkit.js.org/rtk-query/overview (redirects to https://redux.js.org/toolkit/rtk-query/overview, fetched 2026-10-08)
