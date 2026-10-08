# Performance

> Load when: slow renders, re-renders, `memo`/`useMemo`/`useCallback`, React Compiler, `lazy`, code splitting, bundle size, long lists, virtualization, `key`. Pinned: React 19.3, Vite 8, React Compiler 1.0, React Router 8.

## Existing repo
- How to recognise it: compiler on if `babel-plugin-react-compiler` or `reactCompilerPreset` appears in `package.json` or `vite.config`; `react-window` or `@tanstack/react-virtual` in dependencies for lists; the conventions file's `compiler:` line.
- Rule: follow what is there. Keep existing `memo`/`useMemo`/`useCallback`: the compiler docs say removing them can change compilation output, so leave them or test carefully before removing.
- Compiler off: memoize only after the React DevTools Profiler shows a component re-rendering often with unchanged props and costly rendering.
- Keep `react-window` if present; do not swap it for TanStack Virtual unasked.

## New repo default
- Compiler on: write plain components; add no new `memo`/`useMemo`/`useCallback`. Exception from the docs: a memoized value used as an effect dependency, to stop an effect firing repeatedly.
- Compiler off: measure first with the Profiler; first try keeping state local and passing JSX as `children`, then `memo`.
- Keys: a stable unique id from the data (database id, or `crypto.randomUUID()` for local items); never the array index for lists that reorder, insert or delete.
- Split code per route with `lazy` + `Suspense`; declare `lazy(...)` at module top level, never inside a component. A rejected import goes to the nearest error boundary.
- Long lists (hundreds of rows or more): virtualize with `@tanstack/react-virtual`.

```tsx
import { lazy, Suspense } from 'react';

const SettingsPage = lazy(() => import('./SettingsPage'));

export function SettingsRoute() {
  return (
    <Suspense fallback={<p role="status">Loading...</p>}>
      <SettingsPage />
    </Suspense>
  );
}
```

## Avoid
- Manual memoization everywhere "just in case" → noise the compiler makes redundant → plain code, measure first.
- Stripping existing `useMemo`/`useCallback` during unrelated work → can change compiler output → leave them or test the removal.
- `key={index}` on reorderable lists → state and DOM attach to the wrong item → a stable id.
- `lazy()` declared inside a component → state resets on re-render → module top level.
- Rendering thousands of rows directly → slow scroll and mount → virtualize.

## Sources
- https://react.dev/learn/react-compiler (fetched 2026-10-08)
- https://react.dev/learn/react-compiler/introduction (fetched 2026-10-08)
- https://react.dev/reference/react/memo (fetched 2026-10-08)
- https://react.dev/reference/react/lazy (fetched 2026-10-08)
- https://react.dev/learn/rendering-lists (fetched 2026-10-08)
- https://tanstack.com/virtual/latest (fetched 2026-10-08)
