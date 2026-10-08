# Detect conventions (existing repo)

> Load when: a dependency manifest (`pyproject.toml`, `requirements*.txt`, `setup.py`, `setup.cfg`, `Pipfile`) lists `anthropic`, `langgraph`, `langchain*`, `claude-agent-sdk`, `mcp` or `fastmcp`, but no conventions file exists. Pinned: model IDs `claude-fable-5-1` (top), `claude-opus-5-5` (upper), `claude-sonnet-5-5` (mid), `claude-haiku-5-5` (small); anthropic 1.x, langgraph 1.x, langchain-anthropic 1.x, langchain-core 1.x, mcp 2.x, claude-agent-sdk 0.x (verified 2026-10-08).

## Existing repo
- Scope: the project being edited (nearest `pyproject.toml`) plus the repo root. Do not scan sibling projects.
- Read dependency manifests first, then grep imports and config in that scope.
- Rule: record what is there. Never migrate, never "fix" a choice while detecting.
- Signal to field map:

| Signal found | Field and value |
|---|---|
| only `anthropic` imported | `orchestration: anthropic-sdk` |
| `langgraph` imported (`StateGraph`, `create_agent`) | `orchestration: langgraph` |
| `claude_agent_sdk` imported | `orchestration: claude-agent-sdk` |
| more than one of the above | `orchestration: mixed` |
| model ID strings in code, settings or env | `models:` one entry per role (router, main, hard) |
| `InMemorySaver`, `SqliteSaver`, `PostgresSaver` (sync or async) | `checkpointer: memory / sqlite / postgres` |
| no checkpointer passed to `compile()` | `checkpointer: none` |
| `InMemoryStore`, `PostgresStore` | `store: langgraph-store` |
| memory tool usage (a `memory` tool type in requests) | `store: memory-tool` |
| `cache_control` in requests | `caching: on` (else `off`) |
| `pgvector`, `langchain-postgres`, any other vector store dependency | `rag: <store name>` (else `none`) |
| `MCPServer`, `FastMCP` or `mcp.server` | `mcp: server` |
| `ClientSession`, `from mcp import Client`, `langchain-mcp-adapters`, `langchain.mcp` / `MCPAdapter`, `mcp_servers=` (API connector) | `mcp: client` (both present: `both`) |
| `LANGSMITH_*` env, `langsmith` | `tracing: langsmith` |
| `langfuse`, or OpenTelemetry GenAI instrumentation | `tracing: langfuse` / `otel` |
| eval folder, `langsmith` evaluate calls | `evals: pytest` or `langsmith` |
| FastAPI app serving the graph | `hosting: fastapi` |
| `langgraph.json` | `hosting: langgraph-platform` |

- Nothing found for a field: write the `none` value (or `other` for hosting). Never guess.

## New repo default
Not applicable: an empty project uses the choose-conventions reference. Detection only runs on code that exists.

Write `<repo>/.claude/conventions/ai-workflow.md`, `mode: existing`, then show it to the user and wait for confirmation before the original task continues:

```
---
stack: ai-workflow
mode: existing
updated: 2026-10-08
detected-from: [pyproject.toml, src/app/graph.py]
---
orchestration: langgraph
models: router=claude-haiku-5-5, main=claude-sonnet-5-5
checkpointer: postgres
store: none
caching: on
rag: none
mcp: none
tracing: langsmith
evals: none
hosting: fastapi
```

- `detected-from` lists exactly the files you read, no more.
- Set `updated` to the day you write it.

## Avoid
- Scanning the whole monorepo → slow and mixes projects → scan the nearest project plus the root.
- Inferring a value from comments or a README → they go stale → use imports and config only; say so when they disagree.
- Reading `.env` for keys or model names → secret files are off limits → read `.env.example` key names or ask the user.
- Writing the file without showing it → the user never confirms the mode → show it and wait.

## Sources
- https://docs.langchain.com/oss/python/langgraph/persistence (fetched 2026-10-08)
- https://pypi.org/project/anthropic/ (fetched 2026-10-08)
- https://modelcontextprotocol.io/docs/getting-started/intro (fetched 2026-10-08)
