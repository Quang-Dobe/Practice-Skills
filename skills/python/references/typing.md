# Typing

> Load when: type hints, annotations, generics, `Protocol`, `TypedDict`, mypy, pyright, ty, or type-checker errors. Pinned: Python 3.14, uv 0.12, ruff 0.16, mypy 2.4, pytest 9, pydantic 2.13, FastAPI 0.142, SQLAlchemy 2.1.

## Existing repo
- How to recognise it: `[tool.mypy]` / `mypy.ini`, `pyrightconfig.json` / `[tool.pyright]`, `[tool.ty]` / `ty.toml`, `py.typed`.
- Rule: keep the repo's checker and its strictness; do not raise it unasked. Match the repo's syntax level (`Optional[X]` vs `X | None`) and the declared `requires-python`.

## New repo default
- Modern syntax: `X | None`, built-in generics (`list[int]`, `dict[str, int]`).
- PEP 695 `def f[T](...)` and `type Alias = ...` need Python 3.12 or newer; below that use `TypeVar` and `TypeAlias`.
- `Protocol` for structural typing; `TypedDict` for dict shapes; `Literal` for fixed values; `Self` for fluent returns; `Final` for constants; `@override` on overriding methods.
- mypy: `strict = true` under `[tool.mypy]` in `pyproject.toml`; relax per module with `[[tool.mypy.overrides]]`.
- pyright: `typeCheckingMode` is `off`, `basic`, `standard` or `strict` (in `[tool.pyright]` or `pyrightconfig.json`).
- ty: Beta (Astral announcement, 2025-12-16), configured under `[tool.ty]`; offer it, do not default to it.
- Suppress with `# type: ignore[code]` and a reason; add `warn_unused_ignores = true`.

```python
from typing import Literal, Protocol, Self, TypedDict, override

type Mode = Literal["r", "w"]


class Movie(TypedDict):
    title: str
    year: int


class Closeable(Protocol):
    def close(self) -> None: ...


def first[T](items: list[T]) -> T | None:
    return items[0] if items else None


class Builder:
    name = ""

    def with_name(self, name: str) -> Self:
        self.name = name
        return self

    @override
    def __repr__(self) -> str:
        return f"Builder({self.name!r})"
```

```toml
[tool.mypy]
strict = true
warn_unused_ignores = true
```

## Avoid
- Bare `# type: ignore` → hides every error on the line → `# type: ignore[arg-type]  # reason`.
- `Any` for convenience → turns the checker off for that value → `object`, a `Protocol` or a generic.
- `Optional[X]` and `List[int]` in new code → legacy spelling → `X | None`, `list[int]`.
- Mixing two type checkers in CI → conflicting errors → pick one.

## Sources
- https://typing.python.org/en/latest/ (fetched 2026-10-08)
- https://peps.python.org/pep-0695/ (fetched 2026-10-08)
- https://mypy.readthedocs.io/en/stable/config_file.html (fetched 2026-10-08)
- https://microsoft.github.io/pyright/#/configuration (fetched 2026-10-08)
- https://docs.astral.sh/ty/ (fetched 2026-10-08)
- https://docs.astral.sh/ty/reference/configuration/ (fetched 2026-10-08)
- https://astral.sh/blog/ty (fetched 2026-10-08)
