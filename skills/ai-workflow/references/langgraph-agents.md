# LangGraph agents: tool loop, multi-agent, subgraphs

> Load when: LangGraph tool-calling agents, `ToolNode`, `create_agent`, supervisor, handoffs, subgraphs, multi-agent. Pinned: model IDs `claude-fable-5-1` (top), `claude-opus-5-5` (upper), `claude-sonnet-5-5` (mid), `claude-haiku-5-5` (small); anthropic 1.x, langgraph 1.x, langchain-anthropic 1.x, langchain-core 1.x, mcp 2.x, claude-agent-sdk 0.x (verified 2026-10-08).

## Existing repo
- How to recognise it: `from langchain.agents import create_agent`, or the older `from langgraph.prebuilt import create_react_agent` (still importable in langgraph 1.2, replaced by `create_agent` in v1 per the migration page), or a hand-built loop with `ToolNode` and `tools_condition`.
- Rule: follow what is there. Migration notes if asked: `prompt=` became `system_prompt=`, `pre_model_hook`/`post_model_hook` became middleware.

## New repo default
- Single agent with tools: `create_agent(model, tools=[...], system_prompt=..., checkpointer=...)`; invoke with `{"messages": [...]}` and a `thread_id` config. Pass a `ChatAnthropic` instance (model ID from settings) or a `"provider:model"` string.
- Tools: `@tool` from `langchain.tools`; the docstring is the description and type hints are the schema. Schema and naming advice lives in the tool-design reference.
- Hand-built loop only when you need custom control flow: `llm.bind_tools(tools)` node, `ToolNode(tools)` and `tools_condition` (both from `langgraph.prebuilt`, checked by import on langgraph 1.2), edge `tools -> llm`.
- Approval before write tools: `interrupt` inside the tool or a node (see the permissions reference).
- Multi-agent only when it pays: parallel breadth, context isolation, or separate teams owning components. The docs state a single agent with the right tools and prompt often does as well.
- Patterns named by the docs: subagents (main agent calls subagents as tools), handoffs (tool returns `Command`), skills, router, custom LangGraph workflow.
- Handoff tool: return `Command(goto="sales_agent", update={...messages...}, graph=Command.PARENT)`; include a `ToolMessage` with `runtime.tool_call_id` so the tool call is answered.
- Subgraphs: shared state keys -> pass the compiled subgraph to `add_node`; different schemas -> call `subgraph.invoke` inside a wrapper node that maps state. Subgraph `checkpointer`: `None` per-invocation (default), `True` per-thread, `False` none.

```python
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.memory import InMemorySaver

@tool
def get_order_status(order_id: str) -> str:
    """Look up the shipping status of an order by its ID."""
    return f"Order {order_id}: shipped"

model = ChatAnthropic(model="claude-sonnet-5-5", max_tokens=2048)  # ID from settings in real code
agent = create_agent(
    model,
    tools=[get_order_status],
    system_prompt="You are a support agent. Use tools for order facts.",
    checkpointer=InMemorySaver(),  # Postgres saver in prod
)
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Where is order 42?"}]},
    {"configurable": {"thread_id": "conv-1"}},
)
print(result["messages"][-1].text)
```

## Avoid
- Multi-agent by default → each hop adds model calls and context loss (docs table: handoffs/skills/router take 3 calls for a single request) → start with one agent.
- Tool results trusted as instructions → injection path → treat them as data (guardrails reference).
- Subagent sharing the full parent state when it needs two keys → context bloat → use a private schema with a mapping wrapper.
- New code on `create_react_agent` → superseded in v1 → `create_agent`.
- Passing a `ToolNode` into `create_agent(tools=...)` → the migration page says it no longer accepts `ToolNode` instances → pass the tools.

## Sources
- https://docs.langchain.com/oss/python/langchain/agents (fetched 2026-10-08)
- https://docs.langchain.com/oss/python/langgraph/workflows-agents (fetched 2026-10-08)
- https://docs.langchain.com/oss/python/langchain/multi-agent (fetched 2026-10-08)
- https://docs.langchain.com/oss/python/langchain/multi-agent/handoffs (fetched 2026-10-08)
- https://docs.langchain.com/oss/python/langgraph/use-subgraphs (fetched 2026-10-08)
- https://docs.langchain.com/oss/python/migrate/langchain-v1 (fetched 2026-10-08)
