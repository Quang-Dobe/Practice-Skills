# Python Style

> Load when: writing, editing, renaming, refactoring or reviewing any Python code. Pinned: Python 3.14, uv 0.12, ruff 0.16, mypy 2.4, pytest 9, pydantic 2.13, FastAPI 0.142, SQLAlchemy 2.1.

## Existing repo
- How to recognise it: `[tool.ruff]`, `[tool.black]`, `.flake8`, `.editorconfig`, and the docstring style of nearby code.
- Rule: follow what is there (line length, quotes, docstring style); the formatter config wins over PEP 8.

## New repo default
- Names: `snake_case` functions, variables and modules; `PascalCase` classes; `UPPER_SNAKE` constants; `_private` for internal names.
- Docstrings: PEP 257, triple double quotes, imperative one-line summary ("Return X"). One style per repo (Google or NumPy); follow the repo.
- Imports: absolute imports, three groups (stdlib, third-party, local) sorted by the linter (ruff `I` rules via `ruff check --fix`, or isort; `ruff format` does not sort imports), no wildcard imports.
- `pathlib.Path` over `os.path`; context managers (`with`) for files, locks and connections; f-strings for formatting.
- Comprehensions only while they stay readable; use a loop when it needs nesting or side effects.
- `is None` / `is not None`, never `== None`; no mutable default arguments.
- PEP 8 line limit is 79; keep the project's configured length if it differs.

```python
from pathlib import Path

MAX_LINES = 1000


def read_lines(path: Path, limit: int | None = None) -> list[str]:
    """Return stripped lines of a text file, at most `limit` of them."""
    with path.open(encoding="utf-8") as handle:
        lines = [line.strip() for line in handle]
    if limit is not None:
        return lines[:limit]
    return lines[:MAX_LINES]


def add_tag(tag: str, tags: list[str] | None = None) -> list[str]:
    """Return a new list with `tag` appended."""
    return [*(tags or []), tag]
```

## Avoid
- `def f(items=[])` → the default is shared across calls → use `None` and create the list inside.
- `from module import *` → hides where names come from → import names explicitly.
- `os.path.join(a, b)` in new code → string juggling → `Path(a) / b`.
- `if x == None` → equality can be overridden → `if x is None`.
- Bare `except:` → swallows `KeyboardInterrupt` → catch the narrowest exception.

## Sources
- https://peps.python.org/pep-0008/ (fetched 2026-10-08)
- https://peps.python.org/pep-0257/ (fetched 2026-10-08)
- https://docs.python.org/3/library/pathlib.html (fetched 2026-10-08)
