# Legacy: Class Components and Create React App

> Load when: class components, lifecycle methods (`componentDidMount`, `componentDidUpdate`), `react-scripts`, Create React App, migrating to Vite. Pinned: React 19.3, Vite 8, React Compiler 1.0, React Router 8.

## Existing repo
- How to recognise it: `class X extends Component`/`PureComponent`, `this.setState`, `componentDidMount`/`componentDidUpdate`/`componentWillUnmount`; CRA has `react-scripts` in `package.json`, `public/index.html`, `REACT_APP_*` env vars, Jest via `react-scripts test`.
- Rule: follow what is there. Fix the bug in place, in class style. Convert to hooks or leave CRA only when the user asks.

## New repo default
- Convert only on request. React recommends function components for new code; error boundaries still need a class (use `react-error-boundary`).
- Lifecycle → hooks map: `state`/`setState` → `useState`; `componentDidMount` + `componentWillUnmount` → one `useEffect` with cleanup; `componentDidUpdate` → `useEffect` with a dependency array; `contextType` → `useContext`.
- Bugs in place: a `componentDidUpdate` that calls `setState` loops forever without a guard; compare `prevProps`/`prevState` first.
- CRA was deprecated on 2025-02-14 (React blog); it stays in maintenance mode and works with React 19. The blog recommends a framework, or a build tool such as Vite for apps with unusual constraints; this skill covers only the Vite route.
- CRA → Vite, only on request (Vite 8 needs Node 20.19+ or 22.12+):
  1. Install `vite` and `@vitejs/plugin-react`; remove `react-scripts`; add `vite.config.ts` with the `react()` plugin.
  2. Rename `.js` files that contain JSX to `.jsx` (Vite transforms JSX only in `.jsx`/`.tsx` by default); update the entry `src` in `index.html` to match.
  3. Move `public/index.html` to the project root, add `<script type="module" src="/src/index.tsx"></script>`, drop `%PUBLIC_URL%`.
  4. Rename `REACT_APP_*` to `VITE_*`; replace `process.env.REACT_APP_X` with `import.meta.env.VITE_X`. `VITE_*` values are bundled into client code, so no secrets.
  5. Scripts: `"dev": "vite"`, `"build": "vite build"`, `"preview": "vite preview"`.
  6. Jest → Vitest is optional; leave Jest if it works.

```tsx
// Class component, bug fixed in place: guard added, still a class
componentDidUpdate(prevProps: Props) {
  if (prevProps.userId !== this.props.userId) {
    this.setState({ loading: true });
    void this.load(this.props.userId);
  }
}
```

## Avoid
- Converting classes or leaving CRA during an unrelated task → big unreviewed diff → fix in place, mention it in one line.
- A half-done migration (Vite config next to `react-scripts`) → two toolchains → finish every step or none.
- `setState` in `componentDidUpdate` without a prev-props/state check → infinite loop → guard it.
- Copying lifecycles one-to-one into effects → stale or duplicated work → derive during render where possible.
- Keeping `REACT_APP_` names after moving to Vite → undefined at runtime → `VITE_` prefix.

## Sources
- https://react.dev/reference/react/Component (fetched 2026-10-08)
- https://react.dev/blog/2025/02/14/sunsetting-create-react-app (fetched 2026-10-08)
- https://vite.dev/guide/ (fetched 2026-10-08)
- https://vite.dev/guide/env-and-mode (fetched 2026-10-08)
- https://vite.dev/guide/features#jsx (fetched 2026-10-08)
