# Choose conventions (new repo)

> Load when: no AI dependency exists in the repo yet (new project, or a repo adding its first LLM feature). Pinned: model IDs `claude-fable-5-1` (top), `claude-opus-5-5` (upper), `claude-sonnet-5-5` (mid), `claude-haiku-5-5` (small); anthropic 1.x, langgraph 1.x, langchain-anthropic 1.x, langchain-core 1.x, mcp 2.x, claude-agent-sdk 0.x (verified 2026-10-08).

## Existing repo
- How to recognise it: an AI dependency or a conventions file already exists. Then this menu does not apply; use the detect-conventions reference or the file itself.
- Rule: follow what is there; never migrate unasked.

## New repo default
Defaults chosen by the user (2026-10-08). Show one item per area, recommended first, and wait for the user's picks.

| Area | Recommended default | Alternative |
|---|---|---|
| Orchestration | Anthropic SDK for fixed workflows; LangGraph for agents (state, tools, approval) | Claude Agent SDK |
| Models per role | mid `claude-sonnet-5-5` default; small `claude-haiku-5-5` for routing/classification; top `claude-fable-5-1` for hard reasoning | none offered |
| LangChain glue | `langchain-anthropic` `ChatAnthropic` inside LangGraph | raw SDK calls in nodes |
| Short-term memory | checkpointer: in-memory for dev, Postgres for prod | SQLite |
| Long-term memory | LangGraph Store (Postgres) | Anthropic memory tool |
| Caching | on for system prompt + tool definitions | none offered |
| RAG | pgvector + contextual retrieval; embeddings provider per Anthropic docs | other vector store |
| Structured output | strict tool / JSON schema output | none offered |
| Guards | small-tier input screen; tool results untrusted; `interrupt` approval before write/irreversible tools | none offered |
| MCP | official MCP Python SDK, streamable HTTP | stdio for local tools |
| Tracing | LangSmith | OpenTelemetry / Langfuse |
| Evals | pytest-driven suite, fixed datasets, code/LLM graders | LangSmith evaluations |
| Hosting | LangGraph graph served from FastAPI with SSE | LangGraph Platform/Server |

Orchestration decision rule:
- Fixed, known steps: Anthropic SDK workflow.
- Open-ended tool use needing state or approval: LangGraph.
- Local developer-style agent with built-in file/shell tools: Claude Agent SDK.

After the picks, write `<repo>/.claude/conventions/ai-workflow.md` with `mode: new`:

```
---
stack: ai-workflow
mode: new
updated: 2026-10-08
detected-from: []
---
orchestration: langgraph
models: router=claude-haiku-5-5, main=claude-sonnet-5-5, hard=claude-fable-5-1
checkpointer: memory
store: langgraph-store
caching: on
rag: none
mcp: none
tracing: langsmith
evals: pytest
hosting: fastapi
```

- Python tooling (package manager, linting, FastAPI layout) is chosen by the python skill, not here.
- Model IDs come from the models page at write time; recheck them when the menu runs.

## Avoid
- Choosing LangGraph for a fixed three-step flow → extra state machinery for no gain → a plain SDK workflow.
- Picking the top-tier model everywhere → cost and latency → mid default, small for routing, top only where evals demand it.
- Writing the file before the user answers → the defaults are proposals → wait for the picks.
- Mixing in Python tooling choices → owned by the python skill → leave them out.

## Sources
- https://www.anthropic.com/engineering/building-effective-agents (fetched 2026-10-08)
- https://docs.langchain.com/oss/python/langgraph/overview (fetched 2026-10-08)
- https://code.claude.com/docs/en/agent-sdk/overview (fetched 2026-10-08; docs.claude.com redirects to platform.claude.com, then to this URL)
- https://platform.claude.com/docs/en/models/overview (fetched 2026-10-08)
