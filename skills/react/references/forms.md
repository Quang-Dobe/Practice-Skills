# Forms

> Load when: forms, inputs, form validation, submit handling, React Hook Form, TanStack Form, `useActionState`, `useOptimistic`. Pinned: React 19.3, Vite 8, React Compiler 1.0, React Router 8.

## Existing repo
- How to recognise it: `react-hook-form` + `@hookform/resolvers` in `package.json`; `@tanstack/react-form`; `useForm(` imports; or only `useState` per input ("plain").
- React Hook Form present → keep it, resolver included (`zodResolver`, `yupResolver`, ...). TanStack Form present → keep it; do not port forms to React Hook Form.
- Plain `useState` forms → keep that style for small forms; add the new-repo default only to new non-trivial forms.
- Rule: follow what is there.

## New repo default
- React Hook Form + Zod through `@hookform/resolvers/zod` (`npm install react-hook-form zod @hookform/resolvers`). Zod 4 is the current major on zod.dev; it is tested against TypeScript 5.5+ and requires `strict: true`.
- The Zod schema is the single source of the form type: `type FormValues = z.infer<typeof schema>`. Validation rules live only in the schema; JSX shows `errors.<field>?.message`.
- `register('name')` for native inputs; numeric inputs need `register('age', { valueAsNumber: true })`.
- UI-kit inputs that do not expose a ref (MUI, Select, date pickers) → `Controller` with `control` and `render={({ field, fieldState }) => ...}`. Never `register` and `Controller` the same field.
- Schemas with `.default()` or transforms have different input and output types → `useForm<z.input<typeof schema>, unknown, z.output<typeof schema>>`.
- Simple client-side actions (no schema, no per-field errors; SPA, no server actions) → React 19 `useActionState(action, initialState)` returns `[state, formAction, isPending]`; pass `formAction` to `<form action>`.
- Instant feedback while an async action runs → `useOptimistic(value)` returns `[optimistic, setOptimistic]`; call `setOptimistic` inside the form action.

```tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const schema = z.object({
  name: z.string().min(1, 'Required'),
  age: z.number().min(10, 'Must be at least 10'),
});
type FormValues = z.infer<typeof schema>;

export function ProfileForm({ onSave }: { onSave: (v: FormValues) => Promise<void> }) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  return (
    <form onSubmit={handleSubmit(onSave)} noValidate>
      <label>Name <input aria-invalid={!!errors.name} {...register('name')} /></label>
      {errors.name && <p role="alert">{errors.name.message}</p>}
      <label>Age <input type="number" aria-invalid={!!errors.age} {...register('age', { valueAsNumber: true })} /></label>
      {errors.age && <p role="alert">{errors.age.message}</p>}
      <button disabled={isSubmitting}>Save</button>
    </form>
  );
}
```

```tsx
// useActionState: simple action, no schema
const [error, submit, pending] = useActionState(
  async (_prev: string | null, data: FormData) => {
    const ok = await rename(String(data.get('name')));
    return ok ? null : 'Could not save';
  },
  null,
);
// <form action={submit}> ... {error} ... <button disabled={pending}>
```

## Avoid
- One `useState` per field in a non-trivial form → re-renders and hand-rolled validation → React Hook Form + schema.
- Validation rules duplicated in the schema and in JSX (`required`, `minLength` props or `if` checks) → they drift → keep rules in the Zod schema only.
- A hand-written `FormValues` interface next to a schema → two sources of truth → `z.infer`.
- `register` and `Controller` on the same field → double registration → one or the other.
- Server actions or `"use server"` in form examples → out of scope for this SPA skill → client-side `useActionState`.

## Sources
- https://react-hook-form.com/get-started (fetched 2026-10-08)
- https://react-hook-form.com/docs/usecontroller/controller (fetched 2026-10-08)
- https://github.com/react-hook-form/resolvers (fetched 2026-10-08)
- https://tanstack.com/form/latest (fetched 2026-10-08)
- https://zod.dev (fetched 2026-10-08)
- https://react.dev/reference/react/useActionState (fetched 2026-10-08)
- https://react.dev/reference/react/useOptimistic (fetched 2026-10-08)
