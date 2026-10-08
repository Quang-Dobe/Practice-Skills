# Detect Conventions

> Load when: any pyproject.toml, setup.py, setup.cfg, requirements*.txt, Pipfile or .py source files exist but there is no conventions file. Pinned: Python 3.14, uv 0.12, ruff 0.16, mypy 2.4, pytest 9, pydantic 2.13, FastAPI 0.142, SQLAlchemy 2.1.

## Existing repo
- Scope: the Python project being edited (nearest `pyproject.toml`) plus the repo root. Skip `.venv`, `dist`/`build`, `__pycache__`, and non-Python apps.
- Read only the files below; fill `detected-from` with the ones you actually read.
- Rule: record what is there, never what you would prefer. No signal → write the closest value and say it was a guess.

| Signal | Field |
|---|---|
| `requires-python` in `[project]`, `.python-version` | `python` |
| `[project.scripts]` entry that targets a Typer / argparse / Click command | `project-type: cli` |
| `fastapi` in dependencies | `project-type: fastapi-service` |
| Neither, plus a `[build-system]` | `project-type: library` (a real CLI plus `fastapi` → `mixed`; a script that only starts the FastAPI app is not a CLI) |
| `uv.lock` or `[tool.uv]` | `manager: uv` |
| `poetry.lock` or `[tool.poetry]` | `manager: poetry` |
| `requirements*.in` + `.txt` | `manager: pip-tools` |
| plain `requirements.txt` only | `manager: pip` |
| `Pipfile` / `Pipfile.lock` | `manager: pip`, marked as a guess ("Pipenv found") |
| `src/<pkg>/` vs `<pkg>/` at root | `layout: src` vs `flat` |
| feature folders vs `models/ services/ routers/` | `feature` vs `layer` |
| `[tool.ruff]` / `ruff.toml` | `lint-format: ruff` |
| `[tool.black]` + `.flake8` + `[tool.isort]` | `lint-format: black+flake8+isort` |
| `[tool.mypy]` / `mypy.ini` | `types: mypy` |
| `pyrightconfig.json` / `[tool.pyright]` | `types: pyright` |
| `[tool.ty]` / `ty.toml` | `types: ty` |
| none of the three | `types: none` |
| `pytest` in deps / `[tool.pytest.ini_options]` | `tests: pytest` |
| only `unittest` imports | `tests: unittest` |
| `pydantic` / `attrs` imports | `models: pydantic` / `models: attrs`; neither → `models: dataclass` |
| `structlog` import | `logging: structlog`; else `logging: logging` |
| `sqlalchemy` dependency + `alembic.ini` | `db: sqlalchemy+alembic` |

- Poetry projects may declare metadata in `[project]` (modern) or `[tool.poetry]` (older); check both.

## New repo default
Not applicable: a repo with Python files is an existing repo. For an empty repo use the choose-conventions reference.

Write the file, then stop and wait for confirmation:
- Create `.claude/conventions/` if missing.
- Path: `<repo>/.claude/conventions/python.md`, `mode: existing`, `updated:` today.
- Show the file to the user and wait for confirmation before routing the original task.

```
---
stack: python
mode: existing
updated: 2026-10-08
detected-from: [pyproject.toml, uv.lock, ruff.toml]
---
python: 3.12
project-type: fastapi-service
manager: uv
layout: src ; feature
lint-format: ruff
types: mypy
tests: pytest
models: pydantic
logging: logging
db: sqlalchemy+alembic
naming: default
```

## Avoid
- Migrating while detecting → detection only records → write what exists, even if outdated.
- Scanning `.venv`, `dist`, `build` → thousands of foreign files give false signals → skip them.
- Writing the file without showing it → the user cannot correct a wrong guess → wait for a yes.
- Inventing a value with no signal → later tasks trust the file → mark it as a guess.

## Sources
- https://packaging.python.org/en/latest/guides/writing-pyproject-toml/ (fetched 2026-10-08)
- https://docs.astral.sh/uv/concepts/projects/layout/ (fetched 2026-10-08)
- https://python-poetry.org/docs/pyproject/ (fetched 2026-10-08)
