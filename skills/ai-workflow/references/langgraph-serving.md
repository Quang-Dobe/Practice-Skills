# LangGraph serving: streaming and deployment

> Load when: streaming graph output (`stream`, `astream`, stream modes), serving or deploying a graph, LangGraph Platform/Server. Pinned: model IDs `claude-fable-5-1` (top), `claude-opus-5-5` (upper), `claude-sonnet-5-5` (mid), `claude-haiku-5-5` (small); anthropic 1.x, langgraph 1.x, langchain-anthropic 1.x, langchain-core 1.x, mcp 2.x, claude-agent-sdk 0.x (verified 2026-10-08).

## Existing repo
- How to recognise it: `graph.stream(...)` / `astream(...)` with `stream_mode=`, a `langgraph.json` at the repo root (LangGraph Server), or a web app that compiles a graph at startup.
- Rule: follow what is there (stream chunk shape, SSE event names, hosting choice). A tuple-shaped chunk loop stays as is; do not add `version="v2"` unasked.

## New repo default
- Stream modes per the docs: `values` (full state each step), `updates` (per-step deltas), `messages` (LLM tokens plus metadata), `custom` (data your nodes emit), `checkpoints`, `tasks`, `debug`. Pass one mode or a list to `stream`/`astream`.
- `version="v2"` gives one uniform chunk shape `{"type", "ns", "data"}`; without it a mode list yields `(mode, data)` tuples. Use v2 in new code.
- Token streaming: `stream_mode="messages"`; `data` is `(message_chunk, metadata)`.
- Custom events: inside a node, `writer = get_stream_writer()` (`langgraph.config`) then `writer({...})`; read them with mode `custom`.
- Subgraph output: `subgraphs=True`; `ns` tells which subgraph emitted it.
- Self-host default: build and compile the graph once at startup with a Postgres checkpointer (see the persistence reference), run each request with its own `thread_id`, and stream the generator below as SSE. Wiring it into FastAPI belongs to the python skill's fastapi-endpoints reference.
- LangGraph Server (deployed product name now "LangSmith Deployment"): `langgraph.json` names your graphs, `langgraph dev` starts a local in-memory server with Studio, install `langgraph-cli[inmem]` (Python >= 3.11, LangSmith API key). Pick it when you want the managed runtime (threads and assistants model, durable execution, streaming, horizontal scaling per the docs) over running your own. Hosting options per the docs: cloud, self-hosted with control plane, hybrid, standalone Docker/Kubernetes.

```python
import json
from collections.abc import AsyncIterator

def sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"

async def run_events(graph, text: str, thread_id: str) -> AsyncIterator[str]:
    """Yield SSE frames for one graph run; the web layer only wraps this."""
    async for part in graph.astream(
        {"messages": [{"role": "user", "content": text}]},
        {"configurable": {"thread_id": thread_id}},
        stream_mode=["messages", "custom"],
        version="v2",
    ):
        if part["type"] == "messages":
            chunk, _meta = part["data"]
            if chunk.text:
                yield sse("token", {"text": chunk.text})
        elif part["type"] == "custom":
            yield sse("status", part["data"])
    yield sse("done", {})
```

## Avoid
- Compiling the graph (or opening the saver) per request → connection churn and lost setup → compile once at startup, share it.
- Streaming `values` to render tokens → resends full state each step → use `messages`.
- Sharing one `thread_id` across concurrent requests of different users → interleaved state → one thread per conversation.
- Dropping the stream on client disconnect without handling cancellation → orphaned model calls → stop iterating when the client goes away.

## Sources
- https://docs.langchain.com/oss/python/langgraph/streaming (fetched 2026-10-08)
- https://docs.langchain.com/langsmith/deployments (fetched 2026-10-08)
- https://docs.langchain.com/oss/python/langgraph/local-server (fetched 2026-10-08)
