# Prompt caching

> Load when: prompt caching, `cache_control`, the same long prompt or document sent repeatedly, cache hits. Pinned: model IDs `claude-fable-5-1` (top), `claude-opus-5-5` (upper), `claude-sonnet-5-5` (mid), `claude-haiku-5-5` (small); anthropic 1.x, langgraph 1.x, langchain-anthropic 1.x, langchain-core 1.x, mcp 2.x, claude-agent-sdk 0.x (verified 2026-10-08).

## Existing repo
- How to recognise it: `cache_control` keys on system blocks, tool definitions or messages; a top-level `cache_control=` argument; `cache_read_input_tokens` in logs; or `ChatAnthropic` calls whose content blocks carry `cache_control`.
- Rule: keep the breakpoints where they are; check the hit rate before moving them.

## New repo default
- Caching is prefix-based. The prefix is built in the order tools, then system, then messages; a hit needs an identical prefix up to the breakpoint.
- Mark the end of each stable section with `cache_control: {"type": "ephemeral"}`. The docs allow up to 4 breakpoints per request. Writes happen only at breakpoints; reads look backward from a breakpoint at most 20 blocks.
- Minimum cacheable length (docs table): 512 tokens on `claude-fable-5-1`, `claude-opus-5-5`, `claude-sonnet-5-5` and `claude-haiku-5-5`. Shorter prefixes are not cached.
- TTL: 5 minutes by default; `{"type": "ephemeral", "ttl": "1h"}` for 1 hour. Multipliers on base input price: 5-minute write 1.25x, 1-hour write 2x, read 0.1x. Reads cost 0.025x on Fable 5.1 and 0.05x on Opus 5.5 and Sonnet 5.5. The pricing page says a 5-minute cache pays off after one read, a 1-hour cache after two.
- Order stable first, volatile last: tools, system prompt, reference documents, then per-request context and the user turn. Put the breakpoint on the last block whose prefix is identical across requests, not on the varying block.
- Anything that changes earlier in the prefix invalidates later caches: changing tool definitions invalidates tools, system and messages; changing `tool_choice` or images invalidates the messages cache. Keep tool order fixed, and keep timestamps and per-request ids out of the system prompt.
- Automatic caching: add `cache_control={"type": "ephemeral"}` at the top level of `messages.create`; the breakpoint moves to the last cacheable block as the conversation grows. Good for multi-turn chat.
- Measure: `usage.cache_creation_input_tokens` (written), `usage.cache_read_input_tokens` (hit), `usage.input_tokens` (after the last breakpoint). Total input is the sum of the three. `usage.cache_creation` splits writes into `ephemeral_5m_input_tokens` and `ephemeral_1h_input_tokens`.

```python
TOOLS = [  # fixed order, defined once
    {"name": "get_order", "description": "Look up an order by id.",
     "input_schema": {"type": "object",
                      "properties": {"order_id": {"type": "string"}},
                      "required": ["order_id"]},
     "cache_control": {"type": "ephemeral"}},  # breakpoint after the last tool
]
SYSTEM = [
    {"type": "text", "text": STABLE_INSTRUCTIONS_AND_POLICY,
     "cache_control": {"type": "ephemeral"}},  # breakpoint after stable system text
]

resp = client.messages.create(
    model=settings.MODEL_MID, max_tokens=1024,  # from app settings
    tools=TOOLS, system=SYSTEM,
    messages=[{"role": "user", "content": f"Today is {today}. {question}"}],  # volatile last
)
u = resp.usage
log.info("cache write=%s read=%s uncached=%s",
         u.cache_creation_input_tokens, u.cache_read_input_tokens, u.input_tokens)
```

## Avoid
- A timestamp or request id in the system prompt → the prefix changes every call, so nothing hits → move it to the last user turn.
- Reordering or regenerating tool lists per request → invalidates tools, system and messages caches → define tools once in a fixed order.
- Breakpoints on a prefix below the minimum length → not cached (the docs list a minimum) → check `cache_creation_input_tokens` is non-zero.
- A 1-hour TTL for rarely reused prefixes → the write costs 2x for nothing → use the 5-minute default unless reads are spread out.
- Assuming a hit without measuring → cost and latency stay high unnoticed → log the three `usage` fields.
- More than 4 breakpoints, counting the automatic one (it takes one of the 4 slots) → the API returns 400 → use at most 4 in total.

## Sources
- https://platform.claude.com/docs/en/build-with-claude/prompt-caching (fetched 2026-10-08; redirected from docs.claude.com)
- https://platform.claude.com/docs/en/about-claude/pricing (fetched 2026-10-08; redirected from docs.claude.com)
