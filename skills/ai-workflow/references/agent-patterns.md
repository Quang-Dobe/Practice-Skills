# Agent and workflow patterns

> Load when: designing an LLM feature or agent, single prompt vs chain vs agent, workflow patterns (routing, parallel calls, orchestrator-workers, evaluator-optimizer). Pinned: model IDs `claude-fable-5-1` (top), `claude-opus-5-5` (upper), `claude-sonnet-5-5` (mid), `claude-haiku-5-5` (small); anthropic 1.x, langgraph 1.x, langchain-anthropic 1.x, langchain-core 1.x, mcp 2.x, claude-agent-sdk 0.x (verified 2026-10-08).

## Existing repo
- How to recognise it: chained `messages.create` calls (chaining), a classifier call followed by a branch (routing), `asyncio.gather` over calls (parallelization), a loop that calls tools until no `tool_use` (agent), or a LangGraph `StateGraph` with the same shapes.
- Rule: keep the pattern that is there. Add a pattern only when a measured failure needs it.

## New repo default
- Workflows run LLMs and tools through predefined code paths. Agents let the LLM direct its own process and tool use.
- Start with the simplest thing: one call, with retrieval and examples. Add steps only when evals show the gain; the source says to increase complexity only when needed.
- Patterns, each with "use when":
  - Prompt chaining with gates: the task splits into fixed sequential steps; a code check (gate) sits between steps.
  - Routing: distinct input categories need different handling and can be classified accurately.
  - Parallelization, sectioning: independent subtasks run at the same time for speed.
  - Parallelization, voting: the same task runs several times when you need higher confidence.
  - Orchestrator-workers: you cannot predict the subtasks; a central LLM splits and delegates (for example, edits across an unknown number of files).
  - Evaluator-optimizer: clear evaluation criteria exist and iteration measurably improves the result.
  - Autonomous agent loop: open-ended problem, unpredictable step count. Needs stop conditions (maximum iterations) and a token or cost budget.
- Multi-agent systems cost more: Anthropic's research system measured about 15 times the tokens of a chat. Use them only for high-value, parallelizable work.
- Agent-computer interface: give tools as much design effort as prompts (names, descriptions, examples); details live in the tool-design reference.

Routing workflow, small model classifies and mid model answers:

```python
import os
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
MODELS = {  # in real code, load from config
    "router": os.getenv("ROUTER_MODEL", "claude-haiku-5-5"),
    "main": os.getenv("MAIN_MODEL", "claude-sonnet-5-5"),
}
ROUTES = {"billing": "You answer billing questions.", "tech": "You answer technical questions."}

def text_of(msg) -> str:
    return next((b.text for b in msg.content if b.type == "text"), "")

def route(question: str) -> str:
    msg = client.messages.create(
        model=MODELS["router"], max_tokens=1024,  # thinking shares this budget
        system=f"Classify the question. Reply with one word: {', '.join(ROUTES)}.",
        messages=[{"role": "user", "content": question}],
    )
    label = text_of(msg).strip().lower()
    return label if label in ROUTES else "tech"  # gate: fall back on bad output

def answer(question: str) -> str:
    msg = client.messages.create(
        model=MODELS["main"], max_tokens=1024,
        system=ROUTES[route(question)],
        messages=[{"role": "user", "content": question}],
    )
    return text_of(msg)
```

## Avoid
- Starting with an agent framework → hidden prompts and loops are harder to debug → direct SDK calls first.
- An agent loop with no iteration cap or budget → runaway cost → set a maximum iteration count and a token budget.
- Vague delegation to subagents ("research X") → duplicated work → give objective, output format, tools and boundaries.
- Adding a pattern without an eval → no proof it helps → measure the single-call baseline first.

## Sources
- https://www.anthropic.com/engineering/building-effective-agents (fetched 2026-10-08)
- https://www.anthropic.com/engineering/multi-agent-research-system (fetched 2026-10-08)
- https://platform.claude.com/docs/en/build-with-claude/overview (fetched 2026-10-08)
