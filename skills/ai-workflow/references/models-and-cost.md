# Models, cost, latency and Anthropic SDK calls

> Load when: choosing a model, cost, latency, token usage, Batch API, streaming API responses, plain Anthropic Python SDK calls (client setup, retries, timeouts, rate limits). Pinned: model IDs `claude-fable-5-1` (top), `claude-opus-5-5` (upper), `claude-sonnet-5-5` (mid), `claude-haiku-5-5` (small); anthropic 1.x, langgraph 1.x, langchain-anthropic 1.x, langchain-core 1.x, mcp 2.x, claude-agent-sdk 0.x (verified 2026-10-08).

## Existing repo
- How to recognise it: model ID strings in config or code, `anthropic.Anthropic(...)` clients, `max_tokens` values, `usage` logging, `messages.batches`, `.stream(`.
- Rule: keep the models, client options and levers in place. Change a model only with an eval run; recheck IDs against the models page.

## New repo default
- Model per role (IDs from the models page, 2026-10-08):

| Role | Model ID | Choose when |
|---|---|---|
| top | `claude-fable-5-1` | demanding reasoning, long-horizon agentic work, or evals on lower tiers fall short |
| mid (default) | `claude-sonnet-5-5` | everyday coding, agent and enterprise workloads |
| small | `claude-haiku-5-5` | routing, classification, extraction, high volume, sub-agent tasks |

- `claude-opus-5-5` sits between mid and top; the docs start "capability-first" there. Pick by task difficulty and evals; read prices from the pricing page, never hard-code them.
- Client setup: `anthropic.Anthropic()` (or `AsyncAnthropic()`); the key comes from the `ANTHROPIC_API_KEY` environment variable. Create one client and reuse it.
- Retries: the SDK retries connection errors, 408, 409, 429 and >=500 (which covers 529 overloaded) 2 times by default with exponential backoff, honoring `retry-after`. Set `max_retries` on the client or per call with `client.with_options(max_retries=5)`.
- Timeouts: default is 10 minutes; set `timeout` (float or `httpx2.Timeout`). A timeout raises `APITimeoutError` and is retried. For long outputs use streaming; a large non-streaming request raises `ValueError`.
- Rate limits: a 429 carries `retry-after`; limits are token-bucket based, and only uncached input tokens count toward ITPM for most models, so caching raises throughput. Ramp traffic up gradually (acceleration limits). A spend-cap 429 has no `retry-after` and the SDK retries cannot fix it.
- Cost levers: small model for routing and classification; prompt caching (see the prompt-caching reference); Message Batches for non-urgent bulk work (50% off per the pricing page, most batches finish within 1 hour, expire after 24 hours); `max_tokens` budgets; `count_tokens`.
- Latency levers: streaming (`client.messages.stream`, `get_final_message()`), smaller model, shorter outputs, parallel calls. Effort tuning is also a lever within one model.
- Log from each response's `usage`: `input_tokens`, `output_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`, plus `message._request_id`.

```python
import anthropic

client = anthropic.Anthropic(max_retries=3, timeout=60.0)  # key from ANTHROPIC_API_KEY
MODEL = "claude-sonnet-5-5"  # load from config in real code
messages = [{"role": "user", "content": "Summarize our refund policy."}]

est = client.messages.count_tokens(model=MODEL, messages=messages)  # free estimate
print("input estimate:", est.input_tokens)

try:
    msg = client.messages.create(model=MODEL, max_tokens=512, messages=messages)
except anthropic.RateLimitError:
    ...  # retries exhausted: queue and back off, or shed load
except anthropic.APIConnectionError:
    ...  # network problem after retries
except anthropic.APIStatusError as e:
    print(e.status_code, e.response.headers.get("request-id"))
    raise
else:
    u = msg.usage
    print(msg._request_id, u.input_tokens, u.output_tokens,
          getattr(u, "cache_creation_input_tokens", None),
          getattr(u, "cache_read_input_tokens", None))
```

## Avoid
- Hard-coded prices in code or docs → they change → read the pricing page, store none.
- One top-tier model for every call → cost and latency → route by difficulty.
- Own retry loop around the SDK's → multiplied retries → tune `max_retries`, handle only what is left.
- Reusing token counts across models → newer tokenizers count about 30% more for the same text (pricing page) → recount per model.
- Batch API for user-facing requests → results can take up to 24 hours → synchronous calls.

## Sources
- https://platform.claude.com/docs/en/models/overview (fetched 2026-10-08; docs.claude.com/en/docs/about-claude/models/overview redirects here)
- https://platform.claude.com/docs/en/about-claude/models/choosing-a-model (fetched 2026-10-08)
- https://platform.claude.com/docs/en/build-with-claude/batch-processing (fetched 2026-10-08)
- https://platform.claude.com/docs/en/build-with-claude/streaming (fetched 2026-10-08)
- https://platform.claude.com/docs/en/build-with-claude/token-counting (fetched 2026-10-08)
- https://platform.claude.com/docs/en/about-claude/pricing (fetched 2026-10-08)
- https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python (fetched 2026-10-08)
- https://github.com/anthropics/anthropic-sdk-python (fetched 2026-10-08)
- https://platform.claude.com/docs/en/api/errors (fetched 2026-10-08; docs.claude.com/en/api/errors redirects here)
- https://platform.claude.com/docs/en/api/rate-limits (fetched 2026-10-08)
