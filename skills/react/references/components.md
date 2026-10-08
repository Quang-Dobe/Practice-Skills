# Components

> Load when: writing or reviewing any function component, JSX/TSX, props, `children`, composition, refs, `forwardRef`. Pinned: React 19.3, Vite 8, React Compiler 1.0, React Router 8.

## Existing repo
- How to recognise it: `.tsx`/`.jsx` files, `React.FC` or `forwardRef` usage, class components, `react` version in `package.json`.
- Rule: follow what is there. Existing class components stay; React 18 repos keep `forwardRef`; match the repo's props and file naming.

## New repo default
- Function components only; `PascalCase` names (React treats lowercase tags as HTML elements).
- One exported component per file, file named after it (`UserCard.tsx`). Define components at top level, never inside another component.
- Props typed with `<Component>Props` (`type` or `interface`), destructured in the signature, defaults via `=`.
- Plain function signature, not `React.FC`: the docs show props destructured on a plain function, so `FC` adds nothing.
- Composition over configuration: accept `children` and slot props (`header`, `actions`) rather than piles of boolean props.
- `ref` is a regular prop in React 19; `forwardRef` is no longer necessary and will be deprecated.
- Keep render pure: no mutating outer variables, no fetches or subscriptions; side effects go in event handlers (preferred) or effects.

```tsx
import type { ReactNode, Ref } from 'react';

type CardProps = {
  title: string;
  actions?: ReactNode;
  children: ReactNode;
  ref?: Ref<HTMLElement>;
};

export function Card({ title, actions, children, ref }: CardProps) {
  return (
    <section ref={ref} className="card">
      <header>
        <h2>{title}</h2>
        {actions}
      </header>
      {children}
    </section>
  );
}
```

## Avoid
- `React.FC` by default → no benefit over a typed plain function → type the props parameter.
- `forwardRef` in React 19 code → no longer necessary → take `ref` as a prop (keep it only in React 18 repos).
- Boolean-prop explosions (`isPrimary`, `isLarge`, `hasIcon`) → combinatorial and unclear → `children`, slots, or a `variant` union.
- Nested component definitions → slow and buggy per the docs → move to top level and pass props.
- Mutating a module variable during render → breaks purity (Strict Mode renders twice in dev) → derive from props/state.

## Sources
- https://react.dev/learn/your-first-component (fetched 2026-10-08)
- https://react.dev/learn/passing-props-to-a-component (fetched 2026-10-08)
- https://react.dev/learn/keeping-components-pure (fetched 2026-10-08)
- https://react.dev/blog/2024/12/05/react-19 (fetched 2026-10-08)
- https://react.dev/reference/react/forwardRef (fetched 2026-10-08)
