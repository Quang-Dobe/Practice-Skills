# Error boundaries

> Load when: crashes, fallback UI, error boundaries, `react-error-boundary`. Pinned: React 19.3, Vite 8, React Compiler 1.0, React Router 8.

## Existing repo
- How to recognise it: a class with `getDerivedStateFromError` or `componentDidCatch`; `react-error-boundary` in `package.json`; `errorElement` on routes.
- Rule: follow what is there. Keep a hand-written class boundary; do not replace it unasked.

## New repo default
- Boundaries catch errors thrown while rendering. They do not catch event handlers, async code (`setTimeout`/`requestAnimationFrame` callbacks, rejected promises) or the boundary's own errors. Errors thrown inside `startTransition` are caught.
- Use `react-error-boundary` (`ErrorBoundary`) instead of writing a class; React has no function-component boundary.
- Fallback via `FallbackComponent` (or `fallbackRender`); `resetKeys` resets the boundary when a listed value changes; `onError` logs.
- Event-handler or async failures: call `showBoundary` from `useErrorBoundary` to route them to the nearest boundary.
- Place one at the app root as the last resort, plus one per route or per independent widget so one failure leaves the rest usable.
- Report from the root: `createRoot` accepts `onCaughtError` (a boundary caught it), `onUncaughtError` (nothing caught it) and `onRecoverableError`; each gets `(error, errorInfo)` with `componentStack`.

```tsx
import { ErrorBoundary, useErrorBoundary, type FallbackProps } from 'react-error-boundary';

declare function save(): Promise<void>;

function Fallback({ error, resetErrorBoundary }: FallbackProps) {
  return (
    <div role="alert">
      <p>Something went wrong: {error instanceof Error ? error.message : 'unknown error'}</p>
      <button onClick={resetErrorBoundary}>Try again</button>
    </div>
  );
}

function SaveButton() {
  const { showBoundary } = useErrorBoundary();
  return <button onClick={() => save().catch(showBoundary)}>Save</button>;
}

export function Widget({ userId }: { userId: string }) {
  return (
    <ErrorBoundary FallbackComponent={Fallback} resetKeys={[userId]} onError={(e) => console.error(e)}>
      <SaveButton />
    </ErrorBoundary>
  );
}
```

## Avoid
- One boundary only at the root → any crash blanks the whole app → add route or widget boundaries.
- Expecting a boundary to catch a rejected fetch in an event handler → it will not → `useErrorBoundary` or handle locally.
- A new hand-written class boundary in new code → extra code to maintain → `react-error-boundary`.
- Swallowing errors in the fallback → silent failures → report via `onError` or the root `onCaughtError`.

## Sources
- https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary (fetched 2026-10-08)
- https://github.com/bvaughn/react-error-boundary (fetched 2026-10-08)
- https://react.dev/reference/react-dom/client/createRoot (fetched 2026-10-08)
