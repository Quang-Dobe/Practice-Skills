# Observability

> Load when: tracing, debugging agent runs step by step, LangSmith, Langfuse, OpenTelemetry for LLM calls. Pinned: model IDs `claude-fable-5-1` (top), `claude-opus-5-5` (upper), `claude-sonnet-5-5` (mid), `claude-haiku-5-5` (small); anthropic 1.x, langgraph 1.x, langchain-anthropic 1.x, langchain-core 1.x, mcp 2.x, claude-agent-sdk 0.x (verified 2026-10-08).

## Existing repo
- How to recognise it: `LANGSMITH_*` env vars or `langsmith` imports (`traceable`); `langfuse` with `@observe` or a callback handler; `opentelemetry` with `gen_ai.*` attributes or an OTLP exporter.
- Rule: keep the backend already in use (LangSmith, Langfuse, OpenTelemetry) and its naming; never add a second tracer unasked.
- Check where redaction is configured before logging new fields.

## New repo default
- Tracing: LangSmith. LangChain and LangGraph runs trace automatically once `LANGSMITH_TRACING=true` and `LANGSMITH_API_KEY` are set; `LANGSMITH_PROJECT` names the project, `LANGSMITH_ENDPOINT` selects a non-US region.
- Plain Anthropic SDK code: decorate functions with `@traceable` from `langsmith` (`run_type="llm"` for model calls so tokens and latency render; `run_type="tool"` for tools). Nested decorated calls become child runs.
- Per model call, record: model ID, input/output tokens and the cache fields (`cache_creation_input_tokens`, `cache_read_input_tokens`), latency, stop reason.
- Per tool call: name, arguments, result size, error flag. Per graph run: node transitions plus run and thread IDs, passed as trace metadata so a conversation can be found.
- Langfuse (`@observe`, LangChain callback, or OpenTelemetry) and OpenTelemetry GenAI semantic conventions (`gen_ai.request.model`, `gen_ai.usage.input_tokens`; spans for inference, `execute_tool`, `invoke_agent`) are kept when present. The OTel conventions have moved to the `semantic-conventions-genai` repo.
- Redact before export: `LANGSMITH_HIDE_INPUTS=true` / `LANGSMITH_HIDE_OUTPUTS=true`, or a `Client` with `hide_inputs`, `hide_outputs` or a regex `anonymizer`. API keys never enter traces; mask PII (emails, IDs) in prompts and tool results.

```python
import os

import anthropic
from langsmith import traceable

os.environ.setdefault("LANGSMITH_TRACING", "true")  # key comes from the environment
client = anthropic.Anthropic()
MODEL = "claude-sonnet-5-5"  # from settings in real code


@traceable(run_type="llm", name="triage-call")  # call: triage(text, langsmith_extra={"metadata": {"thread_id": tid}})
def triage(text: str) -> str:
    resp = client.messages.create(
        model=MODEL, max_tokens=1024, messages=[{"role": "user", "content": text}]
    )
    return next(b.text for b in resp.content if b.type == "text")


@traceable(run_type="tool", name="lookup_order")
def lookup_order(order_id: str) -> dict:
    return {"id": order_id, "status": "shipped"}
```

## Avoid
- Tracing raw prompts with PII or secrets → traces are stored and shared → hide or anonymize inputs/outputs.
- Logging only the final answer → cannot find which step failed → trace every model call, tool call and node.
- Traces without run or thread IDs → conversations cannot be rebuilt → pass IDs as metadata.
- A second tracer beside the existing one → duplicate spans and cost → extend the one in use.
- Debug tracing left on in production at full volume → cost and exposure → project per environment, sampling per the backend's docs.

## Sources
- https://docs.langchain.com/langsmith/observability-quickstart (fetched 2026-10-08)
- https://docs.langchain.com/langsmith/trace-with-langgraph (fetched 2026-10-08)
- https://docs.langchain.com/langsmith/mask-inputs-outputs (fetched 2026-10-08); https://docs.langchain.com/langsmith/annotate-code (fetched 2026-10-08)
- https://langfuse.com/docs (fetched 2026-10-08)
- https://opentelemetry.io/docs/specs/semconv/gen-ai/ (relocation notice; fetched 2026-10-08)
