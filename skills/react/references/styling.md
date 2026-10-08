# Styling

> Load when: CSS, styling, theming, dark mode, Tailwind, CSS Modules, styled-components, Emotion, shadcn/ui, Radix, MUI, Mantine, Chakra. Pinned: React 19.3, Vite 8, React Compiler 1.0, React Router 8.

## Existing repo
- How to recognise it: `tailwindcss` / `@tailwindcss/vite`; `components.json` + `@radix-ui/*` (shadcn/ui); `*.module.css` files; `styled-components` or `@emotion/react`; `@mui/material`, `@mantine/core`, `@chakra-ui/react`.
- Keep the system in use; never mix a second one into the same component tree.
- CSS Modules: keep `*.module.css`; `import styles from './x.module.css'` returns the class-name map.
- CSS-in-JS (styled-components, Emotion): keep and extend; not offered for new repos. Maintenance: the styled-components site (fetched 2026-10-08) shows a post dated 2026-04-10 and no maintenance-mode notice; the Emotion intro page states no maintenance status. No other status claim is made.
- MUI / Mantine / Chakra: recognise them and theme only through the kit's own theme API (MUI `createTheme` + `ThemeProvider`, Mantine `MantineProvider`, Chakra's theme system). Chakra's site shows the 3.x series.
- Rule: follow what is there.

## New repo default
- Tailwind CSS through the Vite plugin: `npm install tailwindcss @tailwindcss/vite`, add `tailwindcss()` to `plugins` in `vite.config.ts`, and put `@import "tailwindcss";` in the main CSS file (Tailwind CSS 4.3 per tailwindcss.com, 2026-10-08).
- Design tokens in CSS with `@theme { --color-brand: oklch(0.72 0.11 178); }`; each token generates utilities (`bg-brand`).
- `cn()` helper: `clsx` for conditions, `tailwind-merge` to resolve conflicting utilities.
- shadcn/ui on top: components are copied into the repo (CLI + `components.json`), built on Radix primitives; edit them in place, they are your code.
- Dark mode: class strategy. Add `@custom-variant dark (&:where(.dark, .dark *));` after the import, toggle `.dark` on `<html>`, persist the choice yourself.
- With a UI kit instead, use the kit's own color-scheme API (e.g. Mantine `defaultColorScheme`).

```ts
// src/lib/cn.ts
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

```css
/* src/index.css */
@import "tailwindcss";
@custom-variant dark (&:where(.dark, .dark *));
@theme {
  --color-brand: oklch(0.72 0.11 178);
}
```

## Avoid
- Joining class strings by hand (`` `${a} ${b}` ``) → conflicting utilities both apply → `cn()`.
- Wrapping or overriding shadcn/ui components from outside → fights the source → edit the copied file.
- Introducing styled-components or Emotion in a new repo → not an offered default → Tailwind or CSS Modules.
- Styling a UI-kit component with ad-hoc CSS overrides → breaks on kit upgrades → the kit's theme API.
- Two styling systems in one component → unpredictable cascade → the repo's existing one.

## Sources
- https://tailwindcss.com/docs/installation/using-vite (fetched 2026-10-08)
- https://tailwindcss.com/docs/theme (fetched 2026-10-08)
- https://tailwindcss.com/docs/dark-mode (fetched 2026-10-08)
- https://ui.shadcn.com/docs (fetched 2026-10-08)
- https://vite.dev/guide/features#css-modules (fetched 2026-10-08)
- https://styled-components.com (fetched 2026-10-08)
- https://emotion.sh (fetched 2026-10-08)
- https://mui.com/material-ui/ (fetched 2026-10-08)
- https://mantine.dev (fetched 2026-10-08)
- https://chakra-ui.com (fetched 2026-10-08)
