# HTTP clients

> Load when: outbound HTTP calls, httpx, requests, timeouts on calls, retries, tenacity. Pinned: Python 3.14, uv 0.12, ruff 0.16, mypy 2.4, pytest 9, pydantic 2.13, FastAPI 0.142, SQLAlchemy 2.1.

## Existing repo
- Recognise it: `import requests` / `import httpx` / `aiohttp`, `requests.Session`, `urllib3.Retry` adapters, tenacity or `backoff` decorators, dependency lines in `pyproject.toml`.
- Rule: follow what is there. Keep `requests`; always pass `timeout=` (requests has no default: without it calls never time out) and call `r.raise_for_status()`. Keep the existing retry mechanism.

## New repo default
- httpx; build ONE client per process or scope and reuse it, so connection pooling works. `httpx.Client` in sync code, `httpx.AsyncClient` in async code (`async with`, or `aclose()` at shutdown, e.g. in the FastAPI lifespan).
- Never create a client inside a loop or per request.
- httpx default timeout is 5 s of network inactivity. Set it explicitly: `httpx.Timeout(10.0, connect=5.0)` gives 10 s for read/write/pool and 5 s for connect. `timeout=None` disables timeouts; do not.
- Call `response.raise_for_status()` so 4xx/5xx raise `httpx.HTTPStatusError`.
- Retries with tenacity: `@retry(stop=stop_after_attempt(n), wait=wait_exponential(...), retry=..., reraise=True)`. Bare `@retry` retries forever on any exception, so always set `stop` and `retry`.
- Retry only retryable failures: timeouts, connection errors, HTTP 429 and 5xx (e.g. 503). Never retry 400/401/403/404, nor non-idempotent POSTs without an idempotency key.
- tenacity decorators also work on `async def` functions.

```python
from typing import Any

import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

RETRY_STATUS = {429, 502, 503, 504}


def _retryable(exc: BaseException) -> bool:
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in RETRY_STATUS
    return isinstance(exc, httpx.TransportError)  # timeouts, connect errors


@retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=0.5, max=10),
    retry=retry_if_exception(_retryable),
    reraise=True,
)
async def get_json(client: httpx.AsyncClient, path: str) -> dict[str, Any]:
    response = await client.get(path)
    response.raise_for_status()
    return response.json()


async def main() -> None:
    timeout = httpx.Timeout(10.0, connect=5.0)
    async with httpx.AsyncClient(base_url="https://api.example.com", timeout=timeout) as client:
        print(await get_json(client, "/items/1"))
```

## Avoid
- `httpx.get(...)` / `requests.get(...)` in a loop → new connection per call, no pooling → one reused client.
- `requests` call without `timeout=` → can hang forever → always pass it.
- Blocking `requests` inside `async def` → stalls the event loop → `httpx.AsyncClient`, or `asyncio.to_thread`.
- Bare `@retry` or retrying every exception → infinite loops, retries on 404 → `stop` + `retry_if_exception`.
- Ignoring the status code → error pages parsed as data → `raise_for_status()`.

## Sources
- https://www.python-httpx.org/advanced/clients/ (fetched 2026-10-08)
- https://www.python-httpx.org/async/ (fetched 2026-10-08)
- https://www.python-httpx.org/advanced/timeouts/ (fetched 2026-10-08)
- https://tenacity.readthedocs.io/ (fetched 2026-10-08)
- https://requests.readthedocs.io/ (fetched 2026-10-08)
- https://requests.readthedocs.io/en/latest/user/quickstart/ (fetched 2026-10-08)
