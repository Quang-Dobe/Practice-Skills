# Choose Conventions

> Load when: an empty repo or new Python project with no conventions file. Pinned: Python 3.14, uv 0.12, ruff 0.16, mypy 2.4, pytest 9, pydantic 2.13, FastAPI 0.142, SQLAlchemy 2.1.

## Existing repo
- How to recognise it: this file does not apply when a `pyproject.toml`, `setup.py`, `setup.cfg`, `requirements*.txt`, `Pipfile` or any `.py` source file exists; use the detect-conventions reference.
- Rule: tools already in the repo are kept, never migrated unasked.

## New repo default
Show this menu, one item per area, recommended first. Defaults chosen by the user (2026-10-08).

| Area | Recommended | Alternatives |
|---|---|---|
| Project type | library, CLI or FastAPI service | mixed |
| Python | current stable 3.14 | an older supported 3.x |
| Manager | uv | poetry; pip + pip-tools |
| Layout | `src/`, feature packages | flat; layer packages |
| Lint + format | ruff | black + flake8 + isort |
| Type checker | mypy `--strict` | pyright; ty (beta) |
| Tests | pytest + pytest-asyncio + pytest-cov | unittest |
| Hooks | pre-commit with ruff + type check | none |
| Models / config | pydantic v2 at boundaries, `dataclass` inside; pydantic-settings | attrs |
| Logging | stdlib `logging` | structlog |
| HTTP | httpx + tenacity | requests |
| Database | SQLAlchemy 2.1 (async) + Alembic | none |
| CLI | Typer | argparse |
| API auth | OAuth2 + JWT, libraries per the FastAPI docs | external IdP / OIDC |
| Container | multi-stage Docker with uv | none |

Then:
- Wait for the user's picks; do not scaffold before they answer.
- Write `<repo>/.claude/conventions/python.md` with `mode: new`, `detected-from: []` and the user's picks, in exactly this format:
- Scaffold with the picked manager. With uv, `uv init` and `uv init --lib` already create a `src/` layout and a build system (uv 0.12 docs).
- CLI project: `uv init my-tool`, then `uv add typer`.

```
---
stack: python
mode: new
updated: YYYY-MM-DD
detected-from: []
---
python: 3.14
project-type: library | cli | fastapi-service | mixed
manager: uv | poetry | pip-tools | pip
layout: src | flat ; feature | layer
lint-format: ruff | black+flake8+isort | <other>
types: mypy | pyright | ty | none
tests: pytest | unittest
models: pydantic | dataclass | attrs
logging: logging | structlog
db: sqlalchemy+alembic | <other> | none
naming: default | <deviations>
```

```
uv init my-service                      # app: src/my_service, [project.scripts], uv_build
uv init --lib my-lib                    # library: adds py.typed, no scripts
uv add "fastapi[standard]"              # FastAPI service
uv add --dev ruff mypy pytest pytest-asyncio pytest-cov pre-commit
uv run fastapi dev                      # dev server
```

## Avoid
- Scaffolding before the user picks → they approve the menu, not your guess → ask first.
- Recommending ty as the default → docs call it Beta → offer it as an alternative only.
- Unquoted extras (`fastapi[standard]`) → some shells expand the brackets → quote them.

## Sources
- https://docs.astral.sh/uv/guides/projects/ (fetched 2026-10-08)
- https://docs.astral.sh/uv/concepts/projects/init/ (fetched 2026-10-08)
- https://docs.astral.sh/ruff/ (fetched 2026-10-08)
- https://mypy.readthedocs.io/en/stable/ (fetched 2026-10-08)
- https://docs.pytest.org/ (fetched 2026-10-08)
- https://fastapi.tiangolo.com/ (fetched 2026-10-08)
- https://astral.sh/blog/ty (fetched 2026-10-08)
