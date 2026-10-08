# Accessibility

> Load when: accessibility, a11y, keyboard use, focus, ARIA, screen readers, modals/dialogs, `jsx-a11y`. Pinned: React 19.3, Vite 8, React Compiler 1.0, React Router 8.

## Existing repo
- How to recognise it: `eslint-plugin-jsx-a11y` in `package.json` or the ESLint config; a UI kit dialog (Radix, MUI, Mantine, Chakra); `axe` tooling.
- Rule: follow what is there. Keep the repo's dialog and UI-kit components; do not swap them for native `<dialog>`.

## New repo default
- Semantic HTML first: `button` for actions, `a` for navigation, `label`, headings, landmarks (`main`, `nav`). Add ARIA only when no native element fits; an accessible name matters more than extra roles.
- Every input has a label (`<label htmlFor>` in JSX); every image has `alt` (empty `alt=""` if decorative).
- Dialogs trap focus and restore it on close: native `<dialog>` opened with `showModal()` does both and closes on Esc; otherwise use the shadcn/ui (Radix) dialog. Always give a close control.
- After a route change, move focus to the new page heading or main region (a ref with `tabIndex={-1}`) so keyboard and screen-reader users are not left on the old link.
- Everything clickable is reachable and operable by keyboard; never put `onClick` on a `div`. Do not rely on pointer-only patterns such as click-outside.
- Add `eslint-plugin-jsx-a11y` (`jsxA11y.flatConfigs.recommended` in flat config). In tests, Testing Library role queries (`getByRole`, `getByLabelText`) double as an a11y check.
- Manual check: Tab, Shift+Tab and Enter through the page.

```tsx
import { useEffect, useId, useRef } from 'react';

export function ConfirmDialog({ open, onClose }: { open: boolean; onClose: () => void }) {
  const ref = useRef<HTMLDialogElement>(null);
  const titleId = useId();
  useEffect(() => {
    const dialog = ref.current;
    if (!dialog) return;
    if (open && !dialog.open) dialog.showModal();
    if (!open && dialog.open) dialog.close();
  }, [open]);
  return (
    <dialog ref={ref} onClose={onClose} aria-labelledby={titleId}>
      <h2 id={titleId}>Delete item?</h2>
      {/* showModal() focuses the first focusable element: Cancel */}
      <button onClick={onClose}>Cancel</button>
    </dialog>
  );
}
```

## Avoid
- `<div onClick>` as a button → no focus, no key support → `<button>`.
- Placeholder as the only label → disappears and is not a name → a real `<label>`.
- `tabIndex` greater than 0 or ARIA that repeats native semantics → breaks tab order → native element.
- Custom modals without focus trap or restore → keyboard users get lost → `<dialog>` or the UI kit dialog.

## Sources
- https://legacy.reactjs.org/docs/accessibility.html (fetched 2026-10-08)
- https://www.w3.org/WAI/ARIA/apg/ (fetched 2026-10-08)
- https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dialog (fetched 2026-10-08)
- https://github.com/jsx-eslint/eslint-plugin-jsx-a11y (fetched 2026-10-08)
