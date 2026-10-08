# Authentication (OIDC SPA)

> Load when: login, logout, tokens, OIDC, OAuth, PKCE, protected pages or routes. Pinned: React 19.3, Vite 8, React Compiler 1.0, React Router 8.

## Existing repo
- How to recognise it: `oidc-client-ts`, `react-oidc-context`, `@auth0/auth0-react`, `@azure/msal-react`, `keycloak-js`, `aws-amplify`, or a cookie session issued by the API (BFF style).
- Rule: follow what is there. Never swap the auth library unasked; do not change where tokens are stored without asking.

## New repo default
- Authorization code flow with PKCE via `oidc-client-ts` + `react-oidc-context`; `response_type` defaults to `code`; PKCE uses S256.
- Tokens in memory: the library default `userStore` is `window.sessionStorage`, so set `userStore` to `new WebStorageStateStore({ store: new InMemoryWebStorage() })`. Any script on the page can read `localStorage`/`sessionStorage`, so one XSS bug would leak the tokens. Cost: a page reload starts a new sign-in redirect.
- `AuthProvider` at the root with `onSigninCallback` removing the `code`/`state` payload from the URL (the docs say it must be provided); `automaticSilentRenew` is on by default.
- `useAuth` gives `isLoading`, `isAuthenticated`, `user`, `error`, `signinRedirect()`, `signoutRedirect()`.
- Protected routes: a wrapper whose effect calls `signinRedirect()` once when not loading, not authenticated and no auth params are in the URL (or the library's `withAuthenticationRequired`). Never redirect during render. This is UX only; the API must enforce auth on every request.
- `redirect_uri` must be a path the router renders (the app root), or the router shows its 404 element. Sign-in lands there; to return to the requested page, pass `signinRedirect({ state: { returnTo } })` and, once authenticated, navigate to `auth.user?.state` with `useNavigate` inside the router.
- Send `user.access_token` as a `Bearer` header from the API client; never put it in URLs.
- Alternative: a BFF (backend-for-frontend). The OAuth browser-app draft (published as RFC 10017) ranks it most secure: the BFF is the confidential OAuth client, keeps tokens server-side, and the SPA uses a Secure, HttpOnly, SameSite cookie. Pick it when you own a backend and the data is sensitive. A pure SPA client is the least secure pattern; use it when no backend is possible.

```tsx
import { InMemoryWebStorage, WebStorageStateStore } from 'oidc-client-ts';
import { AuthProvider, hasAuthParams, useAuth } from 'react-oidc-context';
import { useEffect, useRef, type ReactNode } from 'react';

const oidcConfig = {
  authority: import.meta.env.VITE_OIDC_AUTHORITY,
  client_id: import.meta.env.VITE_OIDC_CLIENT_ID,
  redirect_uri: window.location.origin + '/', // a route the router renders
  userStore: new WebStorageStateStore({ store: new InMemoryWebStorage() }),
  onSigninCallback: () => window.history.replaceState({}, document.title, window.location.pathname),
};

export const Auth = ({ children }: { children: ReactNode }) => (
  <AuthProvider {...oidcConfig}>{children}</AuthProvider>
);

export function RequireAuth({ children }: { children: ReactNode }) {
  const auth = useAuth();
  const tried = useRef(false);
  useEffect(() => {
    if (hasAuthParams() || auth.isAuthenticated || auth.activeNavigator || auth.isLoading || tried.current) return;
    tried.current = true;
    void auth.signinRedirect();
  }, [auth]);
  if (auth.error) return <p role="alert">Sign-in failed: {auth.error.message}</p>;
  if (!auth.isAuthenticated) return <p role="status">Loading…</p>;
  return <>{children}</>;
}
```

## Avoid
- Implicit flow → returns tokens in the URL; the draft strongly discourages it → code flow + PKCE.
- Client secrets in the SPA (or in `VITE_*` vars) → the bundle is public → public client, or a BFF.
- Tokens in `localStorage`/`sessionStorage` → readable by any injected script → in-memory store, or BFF cookies.
- Parsing the JWT by hand to make authorization decisions → the client cannot be trusted → use claims only to shape UI; the API authorizes.
- Treating route guards as security → bypassable in the browser → server-side checks.
- Redirecting without an `isLoading`/`activeNavigator` check → redirect loops → guard first.

## Sources
- https://github.com/authts/oidc-client-ts (fetched 2026-10-08); settings: https://authts.github.io/oidc-client-ts/interfaces/UserManagerSettings.html (fetched 2026-10-08)
- https://github.com/authts/react-oidc-context (README "Adding Automatic Sign-in", `withAuthenticationRequired`; fetched 2026-10-08)
- https://www.rfc-editor.org/info/rfc10017 (RFC 10017, BCP 212; fetched 2026-10-08)
- https://datatracker.ietf.org/doc/html/rfc7636 (fetched 2026-10-08)
