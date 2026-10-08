# LangGraph persistence: checkpointers and Store

> Load when: LangGraph checkpointers, threads, resuming conversations, LangGraph Store. Pinned: model IDs `claude-fable-5-1` (top), `claude-opus-5-5` (upper), `claude-sonnet-5-5` (mid), `claude-haiku-5-5` (small); anthropic 1.x, langgraph 1.x, langchain-anthropic 1.x, langchain-core 1.x, mcp 2.x, claude-agent-sdk 0.x (verified 2026-10-08).

## Existing repo
- How to recognise it: `compile(checkpointer=...)`, `config={"configurable": {"thread_id": ...}}`, imports from `langgraph.checkpoint.*` or `langgraph.store.*`, packages `langgraph-checkpoint-postgres` / `langgraph-checkpoint-sqlite`.
- Rule: follow what is there (saver class, thread-id scheme, store namespaces). Never swap the backend unasked.

## New repo default
- Dev and tests: `InMemorySaver` (`langgraph.checkpoint.memory`). Prod: `PostgresSaver` (`langgraph.checkpoint.postgres`) or `AsyncPostgresSaver` (`langgraph.checkpoint.postgres.aio`) from `langgraph-checkpoint-postgres`. SQLite (`SqliteSaver`, package `langgraph-checkpoint-sqlite`) is the local-file option.
- Call `.setup()` once on a Postgres saver or store to create tables (`await` it for the async saver). A hand-built psycopg connection needs `autocommit=True` and `row_factory=dict_row` (PyPI page); `from_conn_string` handles this. The package installs plain `psycopg`; add `psycopg[binary]` when no libpq is present (import fails with "no pq wrapper available").
- One `thread_id` per conversation, passed as `config={"configurable": {"thread_id": id}}`; keep it under 255 characters for Postgres.
- State history: `graph.get_state(config)`, `graph.get_state_history(config)`. Time travel: invoke `None` with an earlier checkpoint's `config`; `update_state` on it forks.
- Long-term memory: LangGraph Store, `PostgresStore` in prod, `InMemoryStore` in dev. Namespace is a tuple per user, e.g. `("users", user_id, "memories")`; methods `put`, `get`, `search` (plus `aput`/`asearch`).
- Semantic search: `InMemoryStore(index={"embed": embeddings, "dims": N})`, then `search(ns, query=..., limit=k)`. The embeddings provider comes from the RAG decision, not from here.
- Nodes reach the store through the injected `Runtime` parameter: `runtime.store`, with per-run data in `runtime.context` (`context_schema` on the graph).
- Long threads: trim with `trim_messages` inside the model-calling node; `RemoveMessage` deletes, summary nodes compact. Strategy lives in the context-engineering reference.

```python
from dataclasses import dataclass
import uuid
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.runtime import Runtime
from langgraph.store.postgres import PostgresStore

@dataclass
class Context:
    user_id: str
def call_model(state: MessagesState, runtime: Runtime[Context]):
    ns = ("users", runtime.context.user_id, "memories")
    hits = runtime.store.search(ns, query=state["messages"][-1].text, limit=3)
    if fact := extract_fact(state["messages"][-1].text):  # your distiller: clear signals only, strips secrets
        runtime.store.put(ns, str(uuid.uuid4()), {"fact": fact})
    return {"messages": []}  # real code: model call using hits
builder = StateGraph(MessagesState, context_schema=Context)
builder.add_node(call_model)
builder.add_edge(START, "call_model")

DB_URI = "postgresql://user:pass@localhost:5432/app"  # from env in real code
with PostgresSaver.from_conn_string(DB_URI) as saver, PostgresStore.from_conn_string(DB_URI) as store:
    saver.setup()
    store.setup()
    graph = builder.compile(checkpointer=saver, store=store)
    graph.invoke(
        {"messages": [("user", "I prefer short answers")]},
        {"configurable": {"thread_id": "conv-1"}},
        context=Context(user_id="u1"),
    )
```

## Avoid
- `InMemorySaver` in prod → state vanishes on restart and is not shared across workers → Postgres saver.
- Skipping `.setup()` → missing tables → call it once at deploy or startup.
- Reusing one `thread_id` for different users → conversations leak → derive it from user and conversation IDs.
- Storing user facts in checkpoint state → they live only in one thread → write them to the Store.
- Unpickling checkpoints from an untrusted DB → PyPI page advises `LANGGRAPH_STRICT_MSGPACK=true` or an explicit `allowed_msgpack_modules` list.

## Sources
- https://docs.langchain.com/oss/python/langgraph/persistence (fetched 2026-10-08)
- https://docs.langchain.com/oss/python/langgraph/add-memory (fetched 2026-10-08)
- https://docs.langchain.com/oss/python/langgraph/use-time-travel (fetched 2026-10-08)
- https://pypi.org/project/langgraph-checkpoint-postgres/ (fetched 2026-10-08)
