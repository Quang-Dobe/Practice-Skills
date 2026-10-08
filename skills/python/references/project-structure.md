# Project Structure

> Load when: scaffolding a project or package, new module folders, moving files, `src/` layout, `__init__.py`, `pyproject.toml` metadata, entry points, building or publishing. Pinned: Python 3.14, uv 0.12, ruff 0.16, mypy 2.4, pytest 9, pydantic 2.13, FastAPI 0.142, SQLAlchemy 2.1.

## Existing repo
- How to recognise it: `src/<pkg>/` (src layout) or `<pkg>/` beside `pyproject.toml` (flat); `models/ services/ routers/` (layer) vs one folder per feature.
- Rule: follow what is there. Never move a flat repo to `src/` unasked.

## New repo default
- `src/` layout: importable code lives under `src/`, so tests run against the installed package (packaging guide).
- Feature packages (one folder per feature) over layer packages (`models/`, `services/`).
- `__init__.py`: keep it small; explicit re-exports (`__all__`) only for a package's public API; no import side effects.
- `[project]` holds name, version, `requires-python`, dependencies; `[project.scripts]` maps command → `module:function`.
- Build backend: `uv init` writes `uv_build` (uv 0.12 docs); keep the backend a repo already uses.
- Tests in `tests/` beside `src/`, not inside the package.
- Library: `uv init --lib` adds `py.typed`. Build with `uv build`, run `uv build --no-sources` before publishing, then `uv publish`.

```
my-service/
├── pyproject.toml
├── .python-version
├── uv.lock
├── src/
│   └── my_service/
│       ├── __init__.py
│       ├── billing/          # feature package
│       │   ├── __init__.py
│       │   ├── models.py
│       │   └── service.py
│       └── users/
└── tests/
    └── billing/
```

Flat layout (when the repo uses it): `my_service/` sits next to `pyproject.toml` and `tests/`.

```toml
[project]
name = "my-service"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []

[project.scripts]
my-service = "my_service:main"

[build-system]
requires = ["uv_build>=0.12.23,<0.13"]
build-backend = "uv_build"
```

## Avoid
- Layer folders for a growing app → one feature touches five folders → group by feature.
- Heavy code in `__init__.py` → import side effects and cycles → keep it to re-exports.
- Tests inside `src/` → they ship in the wheel → `tests/` beside `src/`.
- Flat layout in a new project → the working directory can shadow the installed package → `src/`.

## Sources
- https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/ (fetched 2026-10-08)
- https://packaging.python.org/en/latest/guides/writing-pyproject-toml/ (fetched 2026-10-08)
- https://docs.astral.sh/uv/concepts/projects/init/ (fetched 2026-10-08)
- https://docs.astral.sh/uv/guides/package/ (fetched 2026-10-08)
