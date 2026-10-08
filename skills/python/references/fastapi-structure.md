# FastAPI Structure

> Load when: New FastAPI app, routers, `APIRouter`, startup/lifespan, `Depends` wiring, settings injection, DB session per request, running or deploying (`fastapi run`, uvicorn). Pinned: Python 3.14, uv 0.12, ruff 0.16, mypy 2.4, pytest 9, pydantic 2.13, FastAPI 0.142, SQLAlchemy 2.1.

## Existing repo
- How to recognise it: `fastapi` in `pyproject.toml` or requirements; `FastAPI(` and `APIRouter(` in `.py` files; optional `[tool.fastapi]` table; a Dockerfile or process file that runs uvicorn/gunicorn.
- Rule: follow what is there. Keep its layout (feature or layer), its startup mechanism and its server command. Do not convert `on_event` handlers or uvicorn commands unasked; new code in a repo that already uses `lifespan` follows it.

## New repo default
- One feature package per area (`users/`, `orders/`), each with its own `router.py` holding an `APIRouter`; `main.py` only builds the app and includes routers.
- `app.include_router(users.router, prefix="/users", tags=["users"])`. Import the submodule (`from app import users`) so router names do not collide.
- Startup/shutdown resources (engine, HTTP client, models) live in a `lifespan` async context manager passed as `FastAPI(lifespan=...)`. Before `yield` = startup, after = shutdown.
- Settings: pydantic-settings `Settings` class, read through an `@lru_cache` getter used with `Depends`, so tests can override it.
- DB session: a `yield` dependency that opens a session per request with `async with`, which closes it. It does not commit: write endpoints call `await session.commit()` before returning, so a failed commit becomes the error response.
- Define `Annotated` aliases once (`SessionDep`, and `SettingsDep = Annotated[Settings, Depends(get_settings)]`) and reuse them in every endpoint. Include routers in `main.py` with `app.include_router(users.router, prefix="/users", tags=["users"])`.
- Entrypoint in `pyproject.toml`: `[tool.fastapi]` `entrypoint = "my_pkg.main:app"`. Run `fastapi dev` locally (reload, 127.0.0.1) and `fastapi run` in production (no reload, 0.0.0.0). Both need `fastapi[standard]`.
- Workers: `fastapi run --workers 4` on a plain host. In containers/Kubernetes run one process per container and scale replicas instead.

```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, FastAPI, Request
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_", extra="ignore")
    database_url: str

@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]  # values come from the environment

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    engine = create_async_engine(get_settings().database_url)
    app.state.sessions = async_sessionmaker(engine, expire_on_commit=False)
    yield
    await engine.dispose()

async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    async with request.app.state.sessions() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]
app = FastAPI(lifespan=lifespan)
```

## Avoid
- `@app.on_event("startup")` → deprecated, and ignored once `lifespan` is set → use `lifespan`.
- `Settings()` built inside each endpoint or at import time → re-reads env, hard to override → `@lru_cache` getter with `Depends`.
- Swallowing an exception in a `yield` dependency's `except` → FastAPI cannot see the error → re-raise, or raise `HTTPException`.
- Global session objects shared across requests → state leaks between requests → one session per request.
- `--workers N` inside Kubernetes pods → duplicates what the orchestrator does → one process per container.

## Sources
- https://fastapi.tiangolo.com/tutorial/bigger-applications/ (fetched 2026-10-08)
- https://fastapi.tiangolo.com/advanced/events/ (fetched 2026-10-08)
- https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/ (fetched 2026-10-08)
- https://fastapi.tiangolo.com/advanced/settings/ (fetched 2026-10-08)
- https://fastapi.tiangolo.com/fastapi-cli/ (fetched 2026-10-08)
- https://fastapi.tiangolo.com/deployment/server-workers/ (fetched 2026-10-08)
