# LangGraph basics: state, nodes, edges

> Load when: LangGraph graphs: `StateGraph`, state, reducers, nodes, edges, conditional routing. Pinned: model IDs `claude-fable-5-1` (top), `claude-opus-5-5` (upper), `claude-sonnet-5-5` (mid), `claude-haiku-5-5` (small); anthropic 1.x, langgraph 1.x, langchain-anthropic 1.x, langchain-core 1.x, mcp 2.x, claude-agent-sdk 0.x (verified 2026-10-08).

## Existing repo
- How to recognise it: `langgraph` in `pyproject.toml`; `from langgraph.graph import StateGraph, START, END`; a `.compile()` call; state declared as `TypedDict`, `MessagesState` subclass or pydantic model.
- Rule: follow what is there (state style, node naming, `Command` vs conditional edges). Never convert one routing style to the other unasked.

## New repo default
- State is a `TypedDict`; keys that accumulate carry a reducer: `Annotated[list, operator.add]`, or `Annotated[list[AnyMessage], add_messages]`. For chat state subclass `MessagesState`.
- Without a reducer a key is overwritten by the latest node update (docs: the default reducer replaces the left value with the right one).
- A node is a function `(state) -> partial update dict`. Return only the keys it changes.
- Fixed branches: `add_edge`. Decision made from state: `add_conditional_edges(node, router)` where `router` returns a node name (annotate `Literal[...]`).
- Decision and update made in the same node: return `Command(update=..., goto=...)` and annotate the return as `Command[Literal[...]]`. Such a node needs no outgoing edge for those targets.
- Always `compile()` before use; call `invoke`/`ainvoke` with the input state.
- Loops are bounded by `recursion_limit` (default 1000 steps per the graph-api page); pass a lower value in `config` and handle `GraphRecursionError` (`langgraph.errors`).
- Small-tier model (`claude-haiku-5-5`) is the default classifier (the snippet's keyword stub stands in for it); keep the model ID in settings.

```python
from typing import Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command

class State(TypedDict):
    question: str
    category: str
    answer: str

def classify(state: State) -> Command[Literal["billing", "tech"]]:
    category = "billing" if "invoice" in state["question"] else "tech"
    return Command(update={"category": category}, goto=category)

def billing(state: State) -> dict:
    return {"answer": f"billing: {state['question']}"}

def tech(state: State) -> dict:
    return {"answer": f"tech: {state['question']}"}

builder = StateGraph(State)
builder.add_node("classify", classify)
builder.add_node("billing", billing)
builder.add_node("tech", tech)
builder.add_edge(START, "classify")
builder.add_edge("billing", END)
builder.add_edge("tech", END)
graph = builder.compile()

result = graph.invoke({"question": "invoice is wrong"}, {"recursion_limit": 25})
```

## Avoid
- Mutating `state` in place → reducers never see the change → return a partial update dict.
- Returning the full state from every node → overwrites keys other branches set → return changed keys only.
- A router returning a name that is not a node → runtime error → annotate `Literal[...]` or pass the path list to `add_conditional_edges`.
- Unbounded agent loops with the default limit → a runaway loop burns 1000 steps → set `recursion_limit` per call.

## Sources
- https://docs.langchain.com/oss/python/langgraph/overview (fetched 2026-10-08)
- https://docs.langchain.com/oss/python/langgraph/graph-api (fetched 2026-10-08)
- https://docs.langchain.com/oss/python/langgraph/use-graph-api (fetched 2026-10-08)
