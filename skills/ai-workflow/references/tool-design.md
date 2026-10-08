# Tool design

> Load when: defining tools for the model, tool names, descriptions, input schemas, tool errors, wrong tool arguments. Pinned: model IDs `claude-fable-5-1` (top), `claude-opus-5-5` (upper), `claude-sonnet-5-5` (mid), `claude-haiku-5-5` (small); anthropic 1.x, langgraph 1.x, langchain-anthropic 1.x, langchain-core 1.x, mcp 2.x, claude-agent-sdk 0.x (verified 2026-10-08).

## Existing repo
- How to recognise it: `tools=[{"name": ..., "input_schema": ...}]` dicts in `messages.create`, `@tool` functions or `args_schema` models (LangChain), `@mcp.tool()` functions, pydantic models used as tool input.
- Rule: keep the naming scheme, schema style and error format already there. Improve descriptions and error text in place; never rename a tool in use without an eval run (names appear in prompts, traces and datasets).

## New repo default
- A client tool has `name` (regex `^[a-zA-Z0-9_-]{1,128}$`), `description`, `input_schema` (JSON Schema); optional `input_examples`, `strict`, `cache_control`, `defer_loading`.
- Description is the biggest lever. Say what the tool does, when to use it and when not, what each parameter means with a format example, and what it does not return. Docs suggest at least 3-4 sentences per tool.
- Design for the agent, not the API: fewer, higher-level tools (one `action` parameter instead of `create_pr`/`review_pr`/`merge_pr`); namespace by service (`github_list_prs`, `slack_send_message`).
- Return only high-signal fields: stable semantic identifiers (slugs, UUIDs), not opaque internals; add pagination, filters, truncation and sensible defaults so one call cannot flood the context.
- Errors are `tool_result` blocks with `is_error: true` and text that says what went wrong and what to try next ("Rate limit exceeded. Retry after 60 seconds."), not `"failed"`.
- Set `strict: true` so tool inputs always match the schema (needs `additionalProperties: false`; same schema subset as structured outputs). Still validate in your handler.
- Define the input as a pydantic model with `extra="forbid"` and pass `model_json_schema()` as `input_schema`; add `input_examples` (schema-valid) for nested or format-sensitive inputs (they cost tokens; not for server tools).
- Evaluate with realistic multi-step tasks from real workflows, read the transcripts, and refine names, descriptions and responses from what the model got wrong.

```python
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, ValidationError

class OrdersSearch(BaseModel):
    model_config = ConfigDict(extra="forbid")  # additionalProperties: false
    customer_id: str = Field(description="Customer slug, e.g. 'acme-corp'. Not an email.")
    status: Literal["open", "shipped", "cancelled"] = Field(description="Order status filter.")

ORDERS_SEARCH = {
    "name": "orders_search",
    "description": (
        "Lists a customer's orders (id, status, total in USD, 20 per call). Use when the user "
        "asks about existing orders. Do not use to create or change orders. Returns no line items."
    ),
    "strict": True,
    "input_schema": OrdersSearch.model_json_schema(),
    "input_examples": [{"customer_id": "acme-corp", "status": "open"}],
}

def run_tool(block, search) -> dict:
    try:
        args = OrdersSearch.model_validate(block.input)
        return {"type": "tool_result", "tool_use_id": block.id, "content": search(args)}
    except ValidationError as e:
        msg = e.errors(include_url=False)[0]["msg"]
        return {"type": "tool_result", "tool_use_id": block.id, "is_error": True,
                "content": f"Invalid input: {msg}. Fix that argument and call again."}
```

## Avoid
- One tool per API endpoint → bigger tool list, more selection mistakes → consolidate into task-level tools.
- Two-word descriptions → the model guesses when and how to call → write what, when, when not, parameter formats.
- Raising exceptions or returning `"failed"` → no recovery hint → `is_error: true` with the cause and the next step.
- Dumping full records → wasted context → return the fields the next step needs, paginate.
- A parameter that asks for the model's "reasoning" → docs warn it may cause a `reasoning_extraction` refusal → ask for a short explanation or evidence.
- Untrusted text (web page, email) returned with no label → see the guardrails reference for tagging and JSON-encoding.

## Sources
- https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview (fetched 2026-10-08; redirected from docs.claude.com)
- https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools (fetched 2026-10-08; the old implement-tool-use URL now serves this page)
- https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls (fetched 2026-10-08)
- https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use (fetched 2026-10-08)
- https://www.anthropic.com/engineering/writing-tools-for-agents (fetched 2026-10-08)
