# Memory

> Load when: remembering facts across turns or sessions, user preferences, long-term memory, memory tool. Pinned: model IDs `claude-fable-5-1` (top), `claude-opus-5-5` (upper), `claude-sonnet-5-5` (mid), `claude-haiku-5-5` (small); anthropic 1.x, langgraph 1.x, langchain-anthropic 1.x, langchain-core 1.x, mcp 2.x, claude-agent-sdk 0.x (verified 2026-10-08).

## Existing repo
- How to recognise it: a LangGraph checkpointer (short-term) or `Store` (long-term), a `memory_20250818` tool entry, a `/memories` directory, a user-facts table in the database, or a vector index of past messages.
- Rule: keep the store and key scheme in place; add the missing layer (short vs long-term) rather than swapping the backend.

## New repo default
- Short-term memory is one thread: conversation state, persisted by a checkpointer so the thread can resume. Long-term memory spans threads: facts, preferences and episodes in namespaced storage.
- Default long-term store: LangGraph Store on Postgres (code lives in the persistence reference). It holds JSON documents under hierarchical namespaces and keys, and supports semantic search and content filtering.
- Store small, explicit facts with a key and a per-user namespace (for example `("users", user_id, "prefs")`). Write on clear signals, not every turn. Writing on the hot path makes a memory available immediately at a latency cost; a background job avoids the latency.
- Users must be able to see and delete their memories. Never store secrets; the memory tool docs say Claude usually refuses to write sensitive data and recommend validation that strips it before your handler writes.
- Retrieval into context: load a bounded set (namespace listing or semantic search top-k) at the start of the turn, inside a tag such as `<memories>`. Recalled text is untrusted data, not instructions.
- Memory tool option: Anthropic's `{"type": "memory_20250818", "name": "memory"}` is client-side. Claude issues `view`, `create`, `str_replace`, `insert`, `delete` and `rename` on paths under `/memories`; your handler runs them against storage you control (a per-user directory or database keys) and returns `tool_result` blocks.
- Handler duties: reject every path outside `/memories` (resolve to canonical form; watch for `../` and URL-encoded variants), cap file sizes, cap characters returned by `view`, expire old files.

```python
import anthropic
from anthropic.tools import BetaLocalFilesystemMemoryTool

client = anthropic.Anthropic()

def reply(user_id: str, text: str):
    memory = BetaLocalFilesystemMemoryTool(base_path=f"./memory/{user_id}")  # one root per user
    runner = client.beta.messages.tool_runner(
        model=settings.MODEL_MID,  # from app settings
        max_tokens=1024,
        messages=[{"role": "user", "content": text}],
        tools=[memory],
    )
    return runner.until_done()
```

## Avoid
- Appending every message to long-term memory → noise and unbounded growth → write distilled facts on clear signals.
- One shared namespace → users see each other's data → namespace by user (and tenant).
- A memory handler that trusts the `path` field → `/memories/../../secrets.env` escapes the directory → validate every path in every command.
- Storing credentials or personal secrets → permanent leak surface → strip before writing; keep secrets in the environment.
- Treating recalled memory as instructions → a poisoned memory steers the agent → mark it as data.
- Using memory as task state → it outlives the task → keep task progress in thread state.

## Sources
- https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool (fetched 2026-10-08; redirected from docs.claude.com)
- https://docs.langchain.com/oss/python/concepts/memory (fetched 2026-10-08)
- https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents (fetched 2026-10-08)
