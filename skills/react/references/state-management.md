# State management

> Load when: shared or global client state, prop drilling, Context, Zustand, Redux Toolkit, Jotai. Pinned: React 19.3, Vite 8, React Compiler 1.0, React Router 8.

## Existing repo
- How to recognise it: `zustand`, `@reduxjs/toolkit` + `react-redux`, or `jotai` in `package.json`; `create(`/`configureStore`/`atom(` calls; the conventions file's `client-state:` line.
- Rule: follow what is there. Keep Redux Toolkit and Jotai; never migrate a store unasked.
- Fetched server data stays out of these stores; use the repo's `server-state` choice.

## New repo default
- Order of choice: local state → lift state to the closest common parent → Context → a store. Stop at the first that fits.
- Context suits low-frequency values such as theme or the current user. Every consumer re-renders when the value changes, so split contexts (state and dispatch, or one per concern).
- Before Context, try passing props or passing JSX as `children` to cut intermediate layers.
- No store until needed; then Zustand, with small slices and selectors so a component subscribes only to what it reads.
- Server data does not belong here: TanStack Query owns it (see the server-state reference).

```tsx
import { create } from 'zustand';

interface UiState {
  sidebarOpen: boolean;
  toggleSidebar: () => void;
}

export const useUiStore = create<UiState>()((set) => ({
  sidebarOpen: false,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
}));

export function SidebarToggle() {
  const open = useUiStore((s) => s.sidebarOpen);
  const toggle = useUiStore((s) => s.toggleSidebar);
  return <button aria-expanded={open} onClick={toggle}>Menu</button>;
}
```

## Avoid
- A global store for state one component owns → needless coupling → `useState`.
- One big Context holding everything → all consumers re-render on any change → split contexts.
- Subscribing to the whole store (`useUiStore()`) → re-renders on every change → select one field.
- Copying fetched data into Zustand, Redux or Jotai → stale duplicate of the cache → read it from the server-state tool.
- Replacing an existing Redux or Jotai setup with Zustand → unasked migration → keep it.

## Sources
- https://react.dev/learn/managing-state (fetched 2026-10-08)
- https://react.dev/learn/passing-data-deeply-with-context (fetched 2026-10-08)
- https://zustand.docs.pmnd.rs (fetched 2026-10-08)
- https://zustand.docs.pmnd.rs/learn/guides/beginner-typescript (fetched 2026-10-08)
- https://redux-toolkit.js.org (redirects to https://redux.js.org/toolkit/, fetched 2026-10-08)
- https://jotai.org (fetched 2026-10-08)
