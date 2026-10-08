# Async

> Load when: `async`/`await`, asyncio, concurrent jobs, `TaskGroup`, timeouts, cancellation. Pinned: Python 3.14, uv 0.12, ruff 0.16, mypy 2.4, pytest 9, pydantic 2.13, FastAPI 0.142, SQLAlchemy 2.1.

## Existing repo
- How to recognise it: `async def`, `import asyncio`, `anyio` or `trio` imports, `pytest-asyncio` / `anyio` test markers, FastAPI routes.
- Rule: follow what is there. If the repo uses `anyio` or `gather`, match it; do not rewrite working concurrency unasked.

## New repo default
- Requires Python 3.11+ for `TaskGroup`, `asyncio.timeout()` and `except*` (fine under the pinned 3.14).
- One entry point: `asyncio.run(main())`. Never call `asyncio.run` inside running async code.
- Structured concurrency with `asyncio.TaskGroup`: if one task fails the rest are cancelled and the errors arrive together as an `ExceptionGroup` (handle with `except*`).
- Deadlines with `async with asyncio.timeout(seconds):`; catch `TimeoutError` outside the block.
- Cancellation: let `asyncio.CancelledError` propagate (it is a `BaseException`); put cleanup in `finally`. If you must suppress it, call `uncancel()`.
- Never block the loop: wrap blocking calls in `await asyncio.to_thread(fn, *args)`; use async clients (httpx.AsyncClient, async DB drivers) for I/O.
- Cap fan-out with `asyncio.Semaphore(n)` used as `async with sem:`.
- Debug blocking or never-awaited coroutines with `asyncio.run(main(), debug=True)` or `PYTHONASYNCIODEBUG=1`.

```python
import asyncio
import time


def blocking_io(n: int) -> int:
    time.sleep(0.1)
    return n * 2


async def worker(n: int, sem: asyncio.Semaphore) -> int:
    async with sem:
        return await asyncio.to_thread(blocking_io, n)


async def main() -> list[int]:
    sem = asyncio.Semaphore(3)
    async with asyncio.timeout(10):
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(worker(i, sem)) for i in range(10)]
    return [t.result() for t in tasks]


if __name__ == "__main__":
    try:
        print(asyncio.run(main()))
    except TimeoutError:
        print("timed out")
```

## Avoid
- Bare `asyncio.create_task(coro())` with no reference → the loop keeps only weak references, so the task can be garbage collected mid-run → keep the task in a set (and `add_done_callback(discard)`) or create it in a `TaskGroup`.
- `asyncio.gather` without error handling when a `TaskGroup` fits → a failure leaves siblings running → `TaskGroup`, or `gather(..., return_exceptions=True)` and inspect each result.
- `time.sleep`, `requests`, sync DB calls inside `async def` → stalls every task → `asyncio.sleep`, async clients, `to_thread`.
- `except asyncio.CancelledError: pass` → breaks cancellation and timeouts → re-raise after cleanup.
- Calling a coroutine without `await` → it never runs (RuntimeWarning) → `await` it or schedule it.
- `asyncio.Semaphore` across OS threads → it is not thread-safe → use it only among tasks of one loop.

## Sources
- https://docs.python.org/3/library/asyncio-task.html (fetched 2026-10-08)
- https://docs.python.org/3/library/asyncio-sync.html (fetched 2026-10-08)
- https://docs.python.org/3/library/asyncio-dev.html (fetched 2026-10-08)
