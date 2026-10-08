# FastAPI Endpoints

> Load when: Adding or changing FastAPI endpoints, request/response models, status codes, exception handlers, background tasks, streaming / SSE. Pinned: Python 3.14, uv 0.12, ruff 0.16, mypy 2.4, pytest 9, pydantic 2.13, FastAPI 0.142, SQLAlchemy 2.1.

## Existing repo
- How to recognise it: `@router.get/post(...)` functions, pydantic models as parameters and `response_model=`/return annotations, `@app.exception_handler`, `StreamingResponse` imports.
- Rule: follow what is there. Keep its error-body shape, model naming and streaming style; do not swap `StreamingResponse` for `fastapi.sse` unasked.

## New repo default
- Separate input and output models (`UserIn` with password, `UserOut` without). Declare the output as the return annotation (`-> UserOut`) or `response_model=` (which wins if both are set); both validate and filter the response.
- Status codes from `fastapi.status` (`status_code=status.HTTP_201_CREATED`). Errors: `raise HTTPException(status_code=404, detail="...")`, never `return`.
- Domain errors: a custom exception class plus `@app.exception_handler(MyError)` returning `JSONResponse`. To catch every HTTP error, register on Starlette's `HTTPException`.
- Validation errors return 422 with `{"detail": [{"loc", "msg", "type", ...}]}`. Override the `RequestValidationError` handler only when the API contract demands another shape; `fastapi.exception_handlers` has the defaults to reuse.
- `async def` when the body awaits async libraries; plain `def` for blocking libraries (FastAPI runs it in a threadpool). Never block inside `async def`.
- `BackgroundTasks.add_task(fn, *args)` for small post-response work (email, log line). Heavy work goes to a queue/worker (the docs name Celery).
- SSE: use `fastapi.sse` (available since FastAPI 0.135): `response_class=EventSourceResponse` on an async generator; each yielded item is JSON-encoded into `data:`. `ServerSentEvent` sets `event`, `id`, `retry`, `raw_data`. Keep-alive pings, `Cache-Control: no-cache` and `X-Accel-Buffering: no` are automatic. Any HTTP method works, so a POST can stream a reply.
- Plain `StreamingResponse(generator, media_type=...)` for non-SSE streams (file or byte chunks, plain-text lines); the generator must `await` (e.g. `await anyio.sleep(0)`) so cancellation works. Use SSE for browser `EventSource` clients and event streams.
- Streaming an agent run: the endpoint only iterates the run's async events and yields them. The agent itself belongs to the ai-workflow skill (its LangGraph serving guidance).

```python
from collections.abc import AsyncIterable

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.sse import EventSourceResponse, ServerSentEvent
from pydantic import BaseModel

router = APIRouter()

class Prompt(BaseModel):
    text: str

async def run_agent(text: str) -> AsyncIterable[str]:  # stand-in for the agent run
    for word in text.split():
        yield word

@router.post("/jobs", status_code=status.HTTP_201_CREATED)
async def create_job(prompt: Prompt, background: BackgroundTasks) -> Prompt:
    background.add_task(print, prompt.text)  # small post-response work
    return prompt

@router.get("/jobs/{job_id}")
async def get_job(job_id: int) -> Prompt:
    raise HTTPException(status_code=404, detail="Job not found")

@router.post("/chat/stream", response_class=EventSourceResponse)
async def chat(prompt: Prompt) -> AsyncIterable[ServerSentEvent]:
    async for token in run_agent(prompt.text):
        yield ServerSentEvent(data=token, event="token")
    yield ServerSentEvent(raw_data="[DONE]", event="done")
```

## Avoid
- Returning the input model that holds a password → leaks secrets → separate output model.
- Blocking calls (sync DB driver, `requests`, `time.sleep`) in `async def` → stalls every request → `def` endpoint or `asyncio.to_thread`.
- Long jobs in `BackgroundTasks` → tied to the app process, lost on restart → queue + worker.
- Raw `StreamingResponse` generators with no `await` → ignore client cancellation → use `fastapi.sse`, or `await anyio.sleep(0)` in the loop.
- A global handler registered only on FastAPI's `HTTPException` → misses Starlette's → register Starlette's class.

## Sources
- https://fastapi.tiangolo.com/tutorial/response-model/ (fetched 2026-10-08)
- https://fastapi.tiangolo.com/tutorial/handling-errors/ (fetched 2026-10-08)
- https://fastapi.tiangolo.com/async/ (fetched 2026-10-08)
- https://fastapi.tiangolo.com/tutorial/background-tasks/ (fetched 2026-10-08)
- https://fastapi.tiangolo.com/advanced/custom-response/ (fetched 2026-10-08)
- https://fastapi.tiangolo.com/tutorial/server-sent-events/ (fetched 2026-10-08)
