# uv and Environments

> Load when: adding or removing dependencies, lockfiles, virtual environments, uv, poetry, pip, pip-tools, Python version. Pinned: Python 3.14, uv 0.12, ruff 0.16, mypy 2.4, pytest 9, pydantic 2.13, FastAPI 0.142, SQLAlchemy 2.1.

## Existing repo
- How to recognise it: `uv.lock` → uv; `poetry.lock` or `[tool.poetry]` → Poetry; `requirements.in` with a compiled `requirements.txt` → pip-tools; only `requirements*.txt` or `Pipfile` → plain pip or Pipenv.
- Rule: detect the manager from the lockfile and use it; never mix managers and never migrate unasked. Never `pip install` into a uv or Poetry project.

| Manager | Add | Remove | Install from lock |
|---|---|---|---|
| uv | `uv add pkg` | `uv remove pkg` | `uv sync`, then `uv run cmd` |
| Poetry | `poetry add pkg` | `poetry remove pkg` | `poetry install` |
| pip-tools | edit `requirements.in`, `pip-compile` | same | `pip-sync` |

## New repo default
- `uv init`, then `uv add <pkg>`; run everything with `uv run <cmd>`.
- Dev-only tools go in a dependency group: `uv add --dev pytest` writes `[dependency-groups] dev = [...]`; more groups with `uv add --group lint ruff`. The `dev` group is synced by default.
- Python version: `requires-python` in `pyproject.toml` sets the supported range; `uv python pin` writes `.python-version` (it wins over `requires-python` when picking the interpreter); `uv python install` fetches one.
- Commit `uv.lock` and `.python-version`.
- CI: `uv sync --locked` fails if the lock is out of date (`--frozen` skips that check and uses the lock as is), then `uv run pytest`.
- Poetry projects: `poetry add --group dev pkg`, `poetry install --no-root` for apps. pip-tools: `pip-compile --upgrade-package name` bumps one pin; commit both files.

```bash
uv init my-service
cd my-service
uv python pin 3.14
uv add httpx pydantic
uv add --dev pytest
uv sync --locked          # CI: fail if uv.lock is stale
uv run pytest
```

## Avoid
- `pip install x` in a uv or Poetry project → the lock and `pyproject.toml` never learn of it → `uv add x` / `poetry add x`.
- Hand-editing `uv.lock`, `poetry.lock` or a compiled `requirements.txt` → drifts from the source of truth → change `pyproject.toml` or `requirements.in`, then re-lock.
- Two lockfiles (`uv.lock` plus `poetry.lock`) → unclear which one wins → one manager.
- Not committing the lockfile → builds differ between machines → commit it.
- Dev tools in `[project.dependencies]` → shipped to users → a dependency group.
- CI with plain `uv sync` → does not fail on a stale lock → `uv sync --locked`.

## Sources
- https://docs.astral.sh/uv/concepts/projects/dependencies/ (fetched 2026-10-08)
- https://docs.astral.sh/uv/concepts/python-versions/ (fetched 2026-10-08)
- https://docs.astral.sh/uv/guides/integration/github/ (fetched 2026-10-08; its example uses `uv sync --locked --all-extras --dev`)
- https://python-poetry.org/docs/cli/ (fetched 2026-10-08)
- https://pip-tools.readthedocs.io/ (fetched 2026-10-08)
