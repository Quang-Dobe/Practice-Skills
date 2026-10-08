# Context engineering

> Load when: long conversations, context-window limits, context-length errors, trimming or summarizing history, compaction. Pinned: model IDs `claude-fable-5-1` (top), `claude-opus-5-5` (upper), `claude-sonnet-5-5` (mid), `claude-haiku-5-5` (small); anthropic 1.x, langgraph 1.x, langchain-anthropic 1.x, langchain-core 1.x, mcp 2.x, claude-agent-sdk 0.x (verified 2026-10-08).

## Existing repo
- How to recognise it: history trimming helpers (`trim_messages`, a slice like `messages[-N:]`), a summarizer call, `context_management=` in API calls, a notes/scratchpad file, or no handling at all.
- Rule: extend the mechanism already there; add measurement (token counts) before replacing a strategy.

## New repo default
- Treat context as a finite budget: the smallest set of high-signal tokens. Accuracy and recall degrade as tokens grow ("context rot"), so more is not automatically better.
- Everything in the request counts: system prompt, tool definitions, every message including tool results, and the output. Tool results are the usual bloat; return only the fields the model needs.
- Strategies, cheapest first:
  - Just-in-time retrieval: keep identifiers (paths, URLs, ids) in context and fetch content with tools when needed instead of preloading.
  - Clear stale tool results with context editing (beta).
  - Compaction: summarize old turns and continue from the summary. The context-windows page names server-side compaction as the primary strategy for long-running conversations (beta, Claude 4.6 and later models).
  - Structured notes outside the window (a file or the memory tool) for state that must survive resets.
  - Sub-agents with clean contexts that return a short summary.
- Measure with the token counting endpoint before sending; it is free but rate-limited, and the count is an estimate.
- Context editing (beta header `context-management-2025-06-27`) goes through `client.beta.messages.create(..., betas=[...])` with `context_management={"edits": [{"type": "clear_tool_uses_20250919", "trigger": {"type": "input_tokens", "value": 30000}, "keep": {"type": "tool_uses", "value": 3}}]}`. Optional keys: `clear_at_least`, `exclude_tools`, `clear_tool_inputs`.

```python
KEEP_TAIL = 6
THRESHOLD = 150_000  # input tokens; tune per model and budget

def compact(client, model: str, system: str, history: list[dict]) -> list[dict]:
    used = client.messages.count_tokens(
        model=model, system=system, messages=history
    ).input_tokens
    if used < THRESHOLD:
        return history
    # tail must start on a plain user turn so roles stay valid
    cut = next((i for i in range(max(0, len(history) - KEEP_TAIL), len(history))
                if history[i]["role"] == "user" and isinstance(history[i]["content"], str)), None)
    if not cut:  # no safe cut point: keep history, rely on context editing
        return history
    old = "\n".join(f"{m['role']}: {m['content']}" for m in history[:cut]
                    if isinstance(m["content"], str))  # tool blocks are skipped
    resp = client.messages.create(
        model=model, max_tokens=4096,  # thinking shares this budget
        messages=[{"role": "user", "content":
                   f"<history>\n{old}\n</history>\nSummarize decisions, facts and open tasks."}],
    )
    summary = next((b.text for b in resp.content if b.type == "text"), None)
    if not summary:
        return history
    return [{"role": "user", "content": f"<summary>\n{summary}\n</summary>"},
            {"role": "assistant", "content": "Noted."}, *history[cut:]]
```

## Avoid
- Preloading whole corpora or full tool outputs → fills the window with low-signal tokens → fetch just in time and trim tool results.
- Counting tokens on one model and reusing the number on another → Claude 4.7 and later models use a tokenizer that yields about 30 percent more tokens for the same text → recount with the model you will call.
- Dropping old turns silently → the agent forgets decisions → summarize, or write notes to external memory first.
- Clearing tool results every turn → invalidates the cached prefix each time → use `trigger` and `clear_at_least` so clearing is rare and worthwhile.
- Treating the overflow error as the control → input over the window returns a 400 "prompt is too long" → count first.

## Sources
- https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents (fetched 2026-10-08)
- https://platform.claude.com/docs/en/build-with-claude/context-editing (fetched 2026-10-08; redirected from docs.claude.com)
- https://platform.claude.com/docs/en/build-with-claude/context-windows (fetched 2026-10-08; redirected)
- https://platform.claude.com/docs/en/build-with-claude/token-counting (fetched 2026-10-08; redirected)
- https://platform.claude.com/docs/en/about-claude/pricing (fetched 2026-10-08)
