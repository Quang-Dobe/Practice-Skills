# Testing LangGraph nodes and graphs

> Load when: testing LangGraph nodes or graphs, fake or mocked models. Pinned: model IDs `claude-fable-5-1` (top), `claude-opus-5-5` (upper), `claude-sonnet-5-5` (mid), `claude-haiku-5-5` (small); anthropic 1.x, langgraph 1.x, langchain-anthropic 1.x, langchain-core 1.x, mcp 2.x, claude-agent-sdk 0.x (verified 2026-10-08).

## Existing repo
- How to recognise it: tests that call node functions directly, `graph.nodes["x"].invoke`, fake chat models from `langchain_core`, or `InMemorySaver`/`MemorySaver` fixtures.
- Rule: follow what is there (fixtures, fake-model helper, test layout). pytest setup and async fixtures belong to the python skill.

## New repo default
- Nodes are plain functions: call them with a hand-built state dict and assert on the returned partial update. No model, no graph.
- Routers (conditional-edge functions) are pure: assert the returned node name per state.
- Graph-level: compile a fresh graph per test with `InMemorySaver()` and a fixed `thread_id`. `graph.nodes["name"].invoke(state)` runs one node of a compiled graph without the checkpointer.
- Fake models from `langchain_core.language_models.fake_chat_models`: `GenericFakeChatModel(messages=iter([...]))` replays `AIMessage`s in order (use `AIMessage(content="", tool_calls=[{"name", "args", "id"}])` to script a tool call); `FakeListChatModel(responses=[...])` replays strings. Both are checked on langchain-core 1.6.
- `bind_tools` raises `NotImplementedError` on the base fake (checked by running it), so subclass it and return `self` before using it with `create_agent` or a `bind_tools` node.
- Approval flow: invoke until `result["__interrupt__"]`, then `graph.invoke(Command(resume=...), same_config)` and assert the outcome. Needs a checkpointer and the same `thread_id`.
- Partial runs: `update_state(config, values, as_node=...)` then `invoke(None, config, interrupt_after=...)` (docs).
- Quality of real model output is checked in the eval suite, not in unit tests; unit tests must pass offline.

```python
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command, interrupt
from langgraph.graph import StateGraph, MessagesState, START
class ScriptedChat(GenericFakeChatModel):
    def bind_tools(self, tools, **kwargs): return self
@tool
def get_weather(city: str) -> str:
    """Return the weather for a city."""
    return f"sunny in {city}"
def test_agent_calls_tool_then_answers():
    model = ScriptedChat(messages=iter([
        AIMessage("", tool_calls=[{"name": "get_weather", "args": {"city": "Hue"}, "id": "c1"}]),
        AIMessage("Sunny in Hue."),
    ]))
    agent = create_agent(model, tools=[get_weather], checkpointer=InMemorySaver())
    out = agent.invoke({"messages": [HumanMessage("weather in Hue?")]}, {"configurable": {"thread_id": "t1"}})
    assert out["messages"][-2].content == "sunny in Hue"  # ToolMessage
    assert out["messages"][-1].content == "Sunny in Hue."
def test_interrupt_then_resume():
    def approve(state: MessagesState):
        return {"messages": [AIMessage("done" if interrupt("Approve?") else "denied")]}
    graph = (StateGraph(MessagesState).add_node("approve", approve)
             .add_edge(START, "approve").compile(checkpointer=InMemorySaver()))
    cfg = {"configurable": {"thread_id": "t2"}}
    assert graph.invoke({"messages": [HumanMessage("go")]}, cfg)["__interrupt__"]
    assert graph.invoke(Command(resume=True), cfg)["messages"][-1].content == "done"
```

## Avoid
- Real-model calls in unit tests → flaky, slow, paid → fakes here, real models in the eval suite.
- One shared checkpointer across tests → state leaks between tests → fresh `InMemorySaver()` per test.
- Scripting more fake responses than the graph consumes (or fewer) → silent pass or `StopIteration` → assert the final messages.
- Asserting on exact model wording from a real model → brittle → use graders in evals.

## Sources
- https://docs.langchain.com/oss/python/langgraph/test (fetched 2026-10-08)
- https://docs.langchain.com/oss/python/langgraph/interrupts (fetched 2026-10-08)
- https://reference.langchain.com/python/langchain_core/ (brief URL on python.langchain.com returns 308 to this reference site; fetched 2026-10-08)
