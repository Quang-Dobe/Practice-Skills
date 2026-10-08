# Tool selection

> Load when: many tools, the model picking the wrong tool, tool search, `tool_choice`. Pinned: model IDs `claude-fable-5-1` (top), `claude-opus-5-5` (upper), `claude-sonnet-5-5` (mid), `claude-haiku-5-5` (small); anthropic 1.x, langgraph 1.x, langchain-anthropic 1.x, langchain-core 1.x, mcp 2.x, claude-agent-sdk 0.x (verified 2026-10-08).

## Existing repo
- How to recognise it: a long `tools=[...]` list or several MCP servers aggregated, `tool_choice=` in calls, `defer_loading`, `tool_search_tool_*` entries, LangGraph tool lists split per node or sub-agent.
- Rule: keep the selection mechanism in place. Add an eval of selection accuracy before changing it; if descriptions overlap, fix names and descriptions first.

## New repo default
- Why selection degrades: every definition is input context, and similar names or overlapping descriptions (`notification-send-user` vs `notification-send-channel`) cause wrong tool or wrong arguments. The tool search page says accuracy degrades past 30-50 tools and a multi-server setup can cost around 55k tokens of definitions. First remedy is fewer tools: consolidate, namespace, write distinct descriptions (see the tool design reference).
- At 10+ tools, definitions over 10k tokens, or growing catalogs, use the server tool search tool: add `{"type": "tool_search_tool_regex_20251119", "name": "tool_search_tool_regex"}` (regex) or the `tool_search_tool_bm25_20251119` variant (natural language), and set `defer_loading: true` on tools to load on demand. Supported on all four pinned models. Under 10 tools with small definitions, skip it.
- Rules from the page: send every definition in `tools` on every request; at least one tool stays non-deferred (never the search tool); keep the 3-5 most used non-deferred; a deferred tool cannot carry `cache_control`. Resend assistant content unchanged, including `server_tool_use` and `tool_search_tool_result`; never return a `tool_result` for a `srvtoolu_...` id.
- Split by domain when one agent still sees too many tools: a router picks a sub-agent or toolset per domain (application design, not an API feature).
- `tool_choice` has four values: `auto` (default with tools), `any` (must call some tool), `tool` (must call the named one), `none`. `{"type": "auto", "disable_parallel_tool_use": true}` allows at most one tool call per turn.
- Forced `any`/`tool` returns a 400 on `claude-opus-5-5`, `claude-sonnet-5-5`, `claude-fable-5-1`, and with manual extended thinking; docs say Haiku 5.5 accepts it with adaptive thinking. Elsewhere use `auto` plus `strict: true` and steer with the system prompt. Changing `tool_choice` invalidates cached message blocks.
- Measure: a fixed task set with the expected tool and arguments, scored on right tool, right arguments, call count; rerun on every description, tool-set or model change. Log which tools the model discovers and refine descriptions from that.

```python
import anthropic

MODEL = "claude-sonnet-5-5"  # from settings, never inline in real code
client = anthropic.Anthropic()

tools = [
    {"type": "tool_search_tool_regex_20251119", "name": "tool_search_tool_regex"},
    {"name": "orders_search", "description": "Lists a customer's orders. Use for order questions.",
     "input_schema": {"type": "object", "properties": {"customer_id": {"type": "string"}},
                      "required": ["customer_id"]}},                       # kept loaded
    {"name": "crm_update_contact", "description": "Updates a CRM contact's fields.",
     "input_schema": {"type": "object", "properties": {"contact_id": {"type": "string"}},
                      "required": ["contact_id"]},
     "defer_loading": True},                                                # found via search
]
resp = client.messages.create(
    model=MODEL, max_tokens=2048, tools=tools,
    tool_choice={"type": "auto", "disable_parallel_tool_use": True},
    messages=[{"role": "user", "content": "Update contact c-17's phone number."}],
)
```


## Avoid
- Setting `defer_loading: true` on every tool or on the search tool → 400 error → keep the search tool and 3-5 core tools loaded.
- `tool_choice` `any`/`tool` on the pinned mid and top models → 400 → `auto` with strict tools.
- Switching `tool_choice` every turn in a cached conversation → message cache misses → keep it stable.
- Adding tools to fix a wrong pick → worse overlap → fix descriptions or merge tools, then re-run the eval.
- Judging selection by eye → regressions go unseen → fixed task set with graded tool calls.

## Sources
- https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool (fetched 2026-10-08; redirected from docs.claude.com)
- https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools (fetched 2026-10-08; the old implement-tool-use URL now serves this page)
- https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview (fetched 2026-10-08)
- https://www.anthropic.com/engineering/advanced-tool-use (fetched 2026-10-08; served as https://www.anthropic.com/news/introducing-advanced-tool-use)
- https://www.anthropic.com/engineering/writing-tools-for-agents (fetched 2026-10-08)
