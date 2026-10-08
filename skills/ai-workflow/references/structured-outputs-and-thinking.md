# Structured outputs and thinking

> Load when: JSON or schema-shaped model output, structured outputs, extended thinking. Pinned: model IDs `claude-fable-5-1` (top), `claude-opus-5-5` (upper), `claude-sonnet-5-5` (mid), `claude-haiku-5-5` (small); anthropic 1.x, langgraph 1.x, langchain-anthropic 1.x, langchain-core 1.x, mcp 2.x, claude-agent-sdk 0.x (verified 2026-10-08).

## Existing repo
- How to recognise it: `output_config=`, `output_format=`, `messages.parse(`, `strict: True` on tools, a single forced tool used as a schema, `with_structured_output(`, `thinking=` or `budget_tokens` in calls.
- Rule: keep the mechanism. `thinking={"type": "enabled", "budget_tokens": N}` returns 400 on the pinned models; tell the user and move to adaptive thinking only after they confirm. The raw `output_format` parameter is deprecated in favour of `output_config.format`.

## New repo default
- JSON outputs: pass `output_config={"format": {"type": "json_schema", "schema": {...}}}`; the reply is JSON text in a `text` block. No beta header needed for this form. All four pinned models are listed as supported.
- Strict tool use: `strict: true` on a tool guarantees its `input` matches the schema; it combines with JSON outputs in one request. With pydantic, `client.messages.parse(..., output_format=Model)` returns `response.parsed_output`; the docs' own helper example uses `output_format=` today.
- Schema subset: `additionalProperties` must be `false`; no recursive schemas, no numeric or string length constraints, `minItems` only 0 or 1. Move such rules into pydantic validators and validate at the boundary anyway. Check `stop_reason` first: `refusal` (200 status) or `max_tokens` may give output that does not match.
- Fallback when the model or feature does not support schema output: a single tool whose `input_schema` is the object, forced with `tool_choice={"type": "tool", "name": ...}`. Forcing is rejected on `claude-opus-5-5`, `claude-sonnet-5-5`, `claude-fable-5-1` (400; docs say Haiku 5.5 accepts it with adaptive thinking); there use `auto` with a strict tool or JSON outputs.
- Thinking on the pinned models is adaptive and on by default; Claude decides when and how much to think. Set depth with `output_config={"effort": ...}`; add `thinking={"type": "adaptive", "display": "summarized"}` to see summaries (default `display` is `"omitted"`).
- Thinking tokens bill as output and count toward `max_tokens`; lower effort first for cost or latency. It helps multi-step reasoning, debugging and long agent runs; skip it for simple extraction or routing (use the small model).
- With tool use, pass every `thinking` block back complete and unmodified with its `tool_use` block in the same turn; edited blocks give a 400. Do not toggle thinking mid-turn.

```python
import anthropic
from pydantic import BaseModel

MODEL = "claude-sonnet-5-5"  # from settings, never inline in real code
client = anthropic.Anthropic()

class Ticket(BaseModel):
    category: str
    urgent: bool
    summary: str

def triage(text: str) -> Ticket:
    resp = client.messages.parse(
        model=MODEL,
        max_tokens=2048,  # thinking shares this budget
        messages=[{"role": "user", "content": f"Triage this ticket:\n<ticket>{text}</ticket>"}],
        output_format=Ticket,
    )
    if resp.stop_reason in ("refusal", "max_tokens"):
        raise ValueError(f"no usable output: {resp.stop_reason}")
    return resp.parsed_output  # the SDK helper validates against the pydantic model
```

## Avoid
- Parsing free text with regex → breaks on wording drift → schema output or a strict tool.
- Trusting schema output without checking `stop_reason` → truncated or refused reply fails the schema → check, then validate.
- `thinking={"type": "enabled", "budget_tokens": ...}` on the pinned models → 400 → adaptive thinking plus `effort`.
- Forced single tool on the pinned mid/top models → 400 → `auto` with strict tool or JSON outputs.
- Dropping or editing thinking blocks between tool turns → 400 or lost reasoning → send them back unchanged.
- Recursive or length-constrained schemas → rejected → flatten the schema, enforce limits in pydantic.

## Sources
- https://platform.claude.com/docs/en/build-with-claude/structured-outputs (fetched 2026-10-08; redirected from docs.claude.com)
- https://platform.claude.com/docs/en/build-with-claude/extended-thinking (fetched 2026-10-08)
- https://platform.claude.com/docs/en/build-with-claude/thinking (fetched 2026-10-08; linked from the extended-thinking page)
- https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools (fetched 2026-10-08; the old implement-tool-use URL now serves this page)
- https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use (fetched 2026-10-08)
