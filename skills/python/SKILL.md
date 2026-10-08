---
name: python
description: Python language, tooling and FastAPI — code style, type hints and type checkers (mypy, pyright, ty), dataclasses and pydantic, asyncio, exceptions and logging, project layout and pyproject.toml, uv/poetry/pip environments, ruff, pytest, Docker, httpx, SQLAlchemy + Alembic, Typer CLIs, and FastAPI apps, endpoints, auth and tests. Use when writing, reviewing, structuring, testing or packaging .py files, editing pyproject.toml, or building a FastAPI service. Not for Django, Flask, pandas/notebook data work, or LangGraph/LangChain, Claude SDK or MCP code.
---

# Python

Pinned: Python 3.14, uv 0.12, ruff 0.16, mypy 2.4, pytest 9, pydantic 2.13, FastAPI 0.142, SQLAlchemy 2.1.
Out of scope: Django and Flask app code (views, models, templates, routes), data-science work (pandas, polars, notebooks, plotting), LangGraph/LangChain, Anthropic/Claude Agent SDK and MCP code (the ai-workflow skill owns those); agent code on other LLM vendors' SDKs is ordinary Python here. Language and tooling tasks (style, typing, uv, ruff, pytest) inside such repos are in scope.
- Whole task out of scope → say so, load no reference, stop.
- Part of the task out of scope (e.g. a FastAPI endpoint that streams a LangGraph run) → route only the in-scope part; name the other skill for the rest.
Not a Python task at all → this skill doesn't apply: load nothing, skip Step 1.

## Step 1 — Mode check (always first)

1. `<repo root>/.claude/conventions/python.md` exists → read it. It overrides every default here and in references.
2. Any `pyproject.toml`, `setup.py`, `setup.cfg`, `requirements*.txt`, `Pipfile` or `.py` source files in the repo but no conventions file → read `references/detect-conventions.md`, scan only the Python project being edited (nearest `pyproject.toml`) plus the repo root — skip `.venv`, build output and non-Python apps — write the conventions file, show it to the user; after the user confirms it, continue to Step 2 for the original task.
3. None anywhere (new project) → read `references/choose-conventions.md`, let the user pick, write the conventions file; after the user picks and the file is written, continue to Step 2 for the original task.
4. Code you are touching contradicts the conventions file → before writing any code, tell the user, ask which wins, update the file; after the answer, continue to Step 2 for the original task.

Step 1 never replaces Step 2: after it, always route the original task.

## Step 2 — Route: read every row whose signal matches the task

| Task signal | Read |
|---|---|
| Writing, editing, renaming, refactoring or reviewing any Python code | `references/python-style.md` |
| Type hints, annotations, generics, `Protocol`, `TypedDict`, mypy, pyright, ty, type-checker errors | `references/typing.md` |
| Data classes, pydantic models, validating input data, settings, environment variables, `.env` config | `references/data-models.md` |
| `async`/`await`, asyncio, concurrent jobs, `TaskGroup`, timeouts, cancellation | `references/async.md` |
| Exceptions, error handling, custom errors, logging, structlog | `references/errors-and-logging.md` |
| Scaffolding a new project or package, new package or module folder, moving files, `src/` layout, `__init__.py`, `pyproject.toml` metadata, entry points, building or publishing a package | `references/project-structure.md` |
| Adding or removing dependencies, lockfiles, virtual environments, uv, poetry, pip, pip-tools, Python version | `references/uv-and-environments.md` |
| ruff, black, flake8, isort, lint/format config, pre-commit hooks | `references/lint-format.md` |
| Writing or running tests (not API tests), pytest, fixtures, parametrize, mocks, coverage | `references/testing.md` |
| Dockerfile, container image | `references/docker.md` |
| Outbound HTTP calls, httpx, requests, timeouts on calls, retries, tenacity | `references/http-clients.md` |
| Database tables, SQLAlchemy, ORM models, queries, sessions, Alembic, migrations | `references/database.md` |
| Command-line tools, subcommands, options, Typer, argparse, Click | `references/cli.md` |
| New FastAPI app, routers, `APIRouter`, startup/lifespan, `Depends` wiring, settings injection, DB session per request, running or deploying (`fastapi run`, uvicorn) | `references/fastapi-structure.md` |
| Adding or changing FastAPI endpoints, request/response models, status codes, exception handlers, background tasks, streaming / SSE | `references/fastapi-endpoints.md` |
| FastAPI auth, OAuth2, JWT, security dependencies, roles, protected endpoints | `references/fastapi-auth.md` |
| Testing FastAPI endpoints, `TestClient`, httpx `AsyncClient`, dependency overrides | `references/fastapi-testing.md` |

Several rows match → read each. No row matches → use the always-rules only; never read references speculatively.

## Always-rules

- Type hints on every public function unless the conventions file says otherwise; no bare `except:`; catch the narrowest exception you can handle.
- No blocking I/O inside `async def`; offload unavoidable blocking calls with `asyncio.to_thread`.
- Validate untrusted input at the boundary with the repo's validation tool (pydantic by default); inside, treat it as validated.
- Add dependencies with the repo's manager; never `pip install` into a uv or poetry project.
- Secrets come from environment/settings, never hard-coded. Never open or commit `.env` files; read key names from `.env.example`.
- Existing repo: keep its tools; never migrate one unasked. New repo: use the user-approved defaults from the choose-conventions reference.
