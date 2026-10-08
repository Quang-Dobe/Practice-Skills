# LangChain chat models: ChatAnthropic

> Load when: LangChain chat models, `ChatAnthropic`, `with_structured_output`, LangChain model settings. Pinned: model IDs `claude-fable-5-1` (top), `claude-opus-5-5` (upper), `claude-sonnet-5-5` (mid), `claude-haiku-5-5` (small); anthropic 1.x, langgraph 1.x, langchain-anthropic 1.x, langchain-core 1.x, mcp 2.x, claude-agent-sdk 0.x (verified 2026-10-08).

## Existing repo
- How to recognise it: `langchain-anthropic` in dependencies; `from langchain_anthropic import ChatAnthropic`, `init_chat_model(...)`, `.bind_tools`, `.with_structured_output`.
- Rule: follow what is there. Keep `init_chat_model` or `ChatAnthropic` as the repo already does; never convert one to the other unasked.

## New repo default
- `ChatAnthropic(model=<id from settings>, max_tokens=...)` inside LangGraph. Mid tier `claude-sonnet-5-5` by default, `claude-haiku-5-5` for routing/classification, `claude-fable-5-1` for hard reasoning.
- API key: `ANTHROPIC_API_KEY` environment variable (the `api_key` param defaults to it). Other documented params: `timeout`, `max_retries`.
- Sampling: the integration page says newer models (`claude-opus-5`, `claude-sonnet-5`) reject non-default sampling parameters and to remove them rather than adjust. Do not set `temperature` on the pinned models.
- Structured output: `model.with_structured_output(Schema, method="json_schema")` with a pydantic `Schema` (the integration page: this enables Anthropic's native structured output). Omitting `method` gives `function_calling`, a forced tool call; the integration page does not say it is rejected, but the Anthropic docs cited in the structured-outputs reference say forcing a tool returns 400 on `claude-opus-5-5`, `claude-sonnet-5-5` and `claude-fable-5-1`, so always pass `json_schema` on the pinned models. `include_raw=True` also returns the raw message. The docs' create_agent `response_format` picks `ProviderStrategy` (native) for Anthropic automatically.
- Tools: `model.bind_tools([tool_a, tool_b], strict=True)`; schema design is in the tool-design reference.
- Prompt caching: put `cache_control={"type": "ephemeral"}` on a content block (system or user text block), or pass `cache_control={"type": "ephemeral", "ttl": "1h"}` to `invoke` as the integration page shows. Cache rules and token minimums are in the prompt-caching reference.
- Thinking: the pinned models use adaptive thinking: `thinking={"type": "adaptive"}` with `effort="medium"` (documented values low, medium, high, xhigh, max) on the constructor. `thinking={"type": "enabled", "budget_tokens": N}` is the older form for Sonnet-and-earlier models and returns 400 on the pinned ones; keep it only where an existing repo already pins an older model. Beta features: `betas=[...]`. Data residency: `inference_geo`.
- Token count before sending: `model.get_num_tokens_from_messages(messages)`.
- Provider-agnostic alternative: `init_chat_model("anthropic:claude-sonnet-5-5")` (same kwargs; `configurable_fields` lets a run switch model).

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel

class Triage(BaseModel):
    category: str
    urgent: bool

MODEL_ID = "claude-haiku-5-5"  # read from settings in real code

model = ChatAnthropic(model=MODEL_ID, max_tokens=2048)  # key from ANTHROPIC_API_KEY; thinking shares max_tokens
triage = model.with_structured_output(Triage, method="json_schema")

system = SystemMessage(content=[
    {"type": "text", "text": "Classify support tickets. <long stable rules>",
     "cache_control": {"type": "ephemeral"}},
])
result = triage.invoke([system, HumanMessage("My invoice is wrong and I am locked out")])
print(result.category, result.urgent)
```

## Avoid
- `thinking` type `enabled` with `budget_tokens` on the pinned models → 400 → `adaptive` plus `effort`.
- Setting `temperature`/sampling params on the pinned models → rejected per the integration page → omit them.
- Model IDs inline across nodes → drift and risky upgrades → one settings value per role.
- `cache_control` on content that changes per request → no cache hits → put it on the stable prefix only.
- Parsing JSON out of free text → brittle → `with_structured_output` or an agent `response_format`.
- Real-model calls in unit tests → slow, flaky, costly → fake models (testing reference), evals for real checks.

## Sources
- https://docs.langchain.com/oss/python/integrations/chat/anthropic (fetched 2026-10-08)
- https://docs.langchain.com/oss/python/langchain/models (fetched 2026-10-08)
- https://docs.langchain.com/oss/python/langchain/structured-output (fetched 2026-10-08)
