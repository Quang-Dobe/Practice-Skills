# FastAPI Testing

> Load when: Testing FastAPI endpoints, `TestClient`, httpx `AsyncClient`, dependency overrides. Pinned: Python 3.14, uv 0.12, ruff 0.16, mypy 2.4, pytest 9, pydantic 2.13, FastAPI 0.142, SQLAlchemy 2.1.

## Existing repo
- How to recognise it: `from fastapi.testclient import TestClient`, `AsyncClient`, `dependency_overrides` in `tests/` or `conftest.py`; an async marker (`anyio` or `asyncio`) in pytest config.
- Rule: follow what is there. Keep its client style, markers and fixtures.

## New repo default
- Sync tests: `TestClient(app)` (needs `httpx`); plain `def test_...`, no `await`.
- Async tests (when the test itself awaits, e.g. DB checks): `httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test")`. New repo (pytest-asyncio, `asyncio_mode = "auto"`): plain `async def test_...`, no marker; do not add the FastAPI docs' `@pytest.mark.anyio`. Repo already on the anyio marker: keep it.
- Lifespan runs only inside `with TestClient(app) as client:`. `AsyncClient` does not trigger it; wrap the app in `LifespanManager` from `asgi-lifespan` when startup is needed.
- Swap dependencies with `app.dependency_overrides[original] = replacement`: DB session, current user, settings (`get_settings`). The key is the original function object. Overrides reach only `Depends` callers: a lifespan that calls `get_settings()` directly ignores them, so for startup values use `monkeypatch.setenv(...)` plus `get_settings.cache_clear()` before `with TestClient(app)`.
- Reset overrides after every test in a fixture (`app.dependency_overrides.clear()`; the docs assign `{}`).
- Override the auth dependency instead of minting tokens, except when testing the auth flow itself.

```python
from collections.abc import Iterator
from typing import Annotated

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

async def get_user() -> str:
    return "real-user"

@app.get("/me")
async def me(user: Annotated[str, Depends(get_user)]) -> dict[str, str]:
    return {"user": user}

@pytest.fixture(autouse=True)
def reset_overrides() -> Iterator[None]:
    yield
    app.dependency_overrides.clear()

def test_me() -> None:
    app.dependency_overrides[get_user] = lambda: "test-user"
    with TestClient(app) as client:  # runs lifespan
        assert client.get("/me").json() == {"user": "test-user"}
```

## Avoid
- `async def` tests that call `TestClient` → it is built for sync tests → `AsyncClient` with `ASGITransport`:
  ```python
  transport = ASGITransport(app=app)  # from httpx import ASGITransport, AsyncClient
  async with AsyncClient(transport=transport, base_url="http://test") as ac:
      assert (await ac.get("/me")).status_code == 200
  ```
- Overrides never reset → leak into later tests → clear in a fixture teardown.
- Expecting startup code to run under `AsyncClient` → resources missing → `LifespanManager`, or a sync `with TestClient`.
- Real external IdP or paid API calls in tests → slow, flaky → override the dependency.
- Patching module internals when a `Depends` seam exists → brittle → `dependency_overrides`.

## Sources
- https://fastapi.tiangolo.com/tutorial/testing/ (fetched 2026-10-08)
- https://fastapi.tiangolo.com/advanced/async-tests/ (fetched 2026-10-08)
- https://fastapi.tiangolo.com/advanced/testing-dependencies/ (fetched 2026-10-08)
