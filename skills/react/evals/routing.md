# React routing evals

Each prompt assumes the `react` skill is loaded. Pass = agent opens every `expect` file, none of the `must-not` files, and shows `behavior` when given. Unless the prompt says otherwise, assume the repo already has .claude/conventions/react.md.

## E01
prompt: Start a new React app in this empty folder.
expect: choose-conventions.md
must-not: detect-conventions.md, legacy-migration.md

## E02
prompt: Repo has package.json with react and vite.config.ts but no .claude/conventions/react.md. Rename the UserCard component to ProfileCard.
expect: detect-conventions.md, components.md
must-not: choose-conventions.md

## E03
prompt: Review this component: `export default function(props: any) { return <span>{props.label}</span> }`
expect: components.md
must-not: server-state.md, testing-e2e.md

## E04
prompt: ProductList copies its props into state with useEffect and then filters them; simplify it.
expect: hooks-and-effects.md
must-not: testing-e2e.md, i18n.md

## E05
prompt: The Dashboard re-renders on every keystroke and its 5,000-row table scrolls slowly.
expect: performance.md
must-not: testing-e2e.md, auth-spa.md

## E06
prompt: If the Reports page crashes, show a fallback with a Retry button instead of a blank screen.
expect: error-boundaries.md
must-not: testing-e2e.md, i18n.md

## E07
prompt: Make the modal dialog usable with the keyboard and keep focus inside it while open.
expect: accessibility.md
must-not: server-state.md

## E08
prompt: Cart items are passed down through five levels of props; share them across the app instead.
expect: state-management.md
must-not: testing-e2e.md

## E09
prompt: Load the orders list from /api/orders, cache it, and refetch it after a new order is created.
expect: server-state.md
must-not: testing-e2e.md, i18n.md

## E10
prompt: Build a signup form with email and password validation and inline error messages.
expect: forms.md
must-not: testing-e2e.md

## E11
prompt: Add a /settings/profile page and keep the selected tab in the URL query string.
expect: routing.md
must-not: testing-e2e.md

## E12
prompt: Switch the button colours to theme tokens and add a dark mode.
expect: styling.md
must-not: server-state.md

## E13
prompt: Proxy /api to localhost:5000 during development and read the API base URL from an env variable.
expect: vite-and-lint.md
must-not: testing-components.md

## E14
prompt: Write a test that clicks Save on ProfileForm and checks the success message, with the API mocked.
expect: testing-components.md
must-not: testing-e2e.md

## E15
prompt: Add a Playwright test for the checkout flow.
expect: testing-e2e.md
must-not: testing-components.md

## E16
prompt: Translate the header into German and French.
expect: i18n.md
must-not: testing-e2e.md

## E17
prompt: Add login with our OIDC provider and protect the /admin pages.
expect: auth-spa.md
must-not: testing-e2e.md

## E18
prompt: This repo still builds with react-scripts; move it to Vite.
expect: legacy-migration.md
must-not: choose-conventions.md

## E19
prompt: Add a Server Component page under app/dashboard in our Next.js app.
expect: none
must-not: components.md, routing.md, detect-conventions.md, choose-conventions.md
behavior: says Next.js / Server Components are out of scope for this skill

## E20
prompt: Add a slugify() helper to packages/core and tighten its tsconfig strict options.
expect: none
must-not: components.md, vite-and-lint.md, detect-conventions.md, choose-conventions.md
behavior: treats it as not a React task (no React reference, no React conventions step)

## E21
prompt: Add a GET /orders endpoint to our ASP.NET Core API.
expect: none
must-not: components.md, detect-conventions.md, choose-conventions.md

## E22
prompt: Add a camera screen to our Expo app.
expect: none
must-not: components.md, detect-conventions.md, choose-conventions.md
behavior: says React Native / Expo are out of scope for this skill

## E23
prompt: .claude/conventions/react.md says "server-state: tanstack-query", but the hooks in the folder I'm editing use SWR. Add a hook that loads invoices.
expect: none
must-not: detect-conventions.md, choose-conventions.md
behavior: flags the mismatch and asks which wins before writing code

## E24
prompt: .claude/conventions/react.md lists "styling: css-modules". Give the Card component a shadow on hover.
expect: styling.md
must-not: detect-conventions.md
behavior: uses CSS Modules; does not propose Tailwind

## E25
prompt: Add an /orders/:id page that loads the order with TanStack Query and shows a fallback UI if rendering fails.
expect: routing.md, server-state.md, error-boundaries.md
must-not: testing-e2e.md

## E26
prompt: Repo root has apps/web (React + Vite, package.json) and services/api (.NET), no .claude/conventions/react.md. Add a Badge component to apps/web.
expect: detect-conventions.md, components.md
must-not: choose-conventions.md
behavior: scopes the convention scan to apps/web and the repo root, not services/api

## E27
prompt: The class component OrderTable loops forever in componentDidUpdate; fix the bug.
expect: legacy-migration.md
must-not: choose-conventions.md
behavior: fixes the class component in place; does not convert it to hooks unasked

## E28
prompt: Add the React hooks lint rules to our ESLint config.
expect: vite-and-lint.md
must-not: testing-components.md

## E29
prompt: Add Storybook stories for each Button variant.
expect: testing-components.md
must-not: testing-e2e.md

## E30
prompt: Replace forwardRef in our TextInput component with the React 19 way of passing refs.
expect: components.md
must-not: server-state.md

## E31
prompt: Read the theme context inside an if-block in Toolbar; the linter complains about useContext there.
expect: hooks-and-effects.md
must-not: testing-e2e.md

## E32
prompt: React Compiler is enabled now. Should we delete our useMemo and useCallback calls?
expect: performance.md
must-not: testing-e2e.md
