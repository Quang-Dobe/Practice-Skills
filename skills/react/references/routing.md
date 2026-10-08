# Routing

> Load when: adding or changing routes (e.g. a new `/settings` URL), route params, navigation, links, search params or URL state, React Router, TanStack Router. Pinned: React 19.3, Vite 8, React Compiler 1.0, React Router 8.

## Existing repo
- How to recognise it: `react-router` (or `react-router-dom`) in `package.json`; `<BrowserRouter>` / `<Routes>` → declarative mode; `createBrowserRouter` + `RouterProvider` → data mode; `@tanstack/react-router` → TanStack Router.
- React Router declarative → keep `<BrowserRouter>`; add routes inside it. Do not move to data mode unasked.
- TanStack Router → keep it; use its type-safe search params (`validateSearch`) for URL state.
- Framework mode (`@react-router/dev`, `react-router.config.ts`) is out of scope: say so and stop.
- Rule: follow what is there.

## New repo default
- React Router data mode: `createBrowserRouter` + `RouterProvider`. Import `createBrowserRouter` and hooks from `react-router`, and `RouterProvider` from `react-router/dom` (per the v8 installation page).
- Create the router once at module level, outside the React tree; never keep it in state.
- Routes are plain objects, one array per feature (`src/features/<name>/routes.tsx`), composed in `src/router.tsx`.
- Route objects use `Component`, `lazy: () => import(...)` for code splitting, and `errorElement` for route-level errors.
- Navigation: `<Link>` / `<NavLink>` for links, `useNavigate` for imperative moves after an action, `useParams` for dynamic segments.
- URL as state: filters, tabs and paging live in `useSearchParams`, not in `useState`.
- SPA hosting: the server must answer unknown paths with `index.html`; configure the production host that way, or deep links return 404.

```tsx
// src/router.tsx
import { createBrowserRouter } from 'react-router';

export const router = createBrowserRouter([
  {
    path: '/',
    Component: RootLayout,
    errorElement: <RouteError />,
    children: [
      { index: true, Component: Home },
      {
        path: 'users/:userId',
        lazy: () => import('./features/users/user-page').then((m) => ({ Component: m.default })),
      },
    ],
  },
]);

// src/main.tsx
// import { RouterProvider } from 'react-router/dom';
// createRoot(el).render(<RouterProvider router={router} />);
```

```tsx
// URL as state
const [params, setParams] = useSearchParams();
const tab = params.get('tab') ?? 'overview';
setParams((p) => { p.set('tab', 'billing'); return p; });
```

## Avoid
- Filters, tabs or page numbers in `useState` → lost on refresh and not shareable → `useSearchParams`.
- Creating the router inside a component or in state → it is rebuilt on render → module-level `createBrowserRouter`.
- Mixing `<BrowserRouter>` and `RouterProvider` → two routers → pick one per app.
- Framework-mode APIs (`@react-router/dev/routes`, `+types`) → out of scope → data-mode route objects.
- Production host without an `index.html` fallback → deep links return 404 → add the SPA fallback rule.

## Sources
- https://reactrouter.com/start/modes (fetched 2026-10-08)
- https://reactrouter.com/start/data/routing (fetched 2026-10-08; its snippet imports from `react-router-dom`, but the installation page below shows v8 imports; the installation page is followed)
- https://reactrouter.com/start/data/installation (fetched 2026-10-08; v8.4.0, imports from `react-router` and `react-router/dom`)
- https://reactrouter.com/api/hooks/useSearchParams (fetched 2026-10-08)
- https://tanstack.com/router/latest (fetched 2026-10-08)
