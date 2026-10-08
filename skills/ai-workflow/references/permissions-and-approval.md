# Permissions and human approval

> Load when: human approval before actions, tool permissions, `interrupt`, `Command(resume=...)`. Pinned: model IDs `claude-fable-5-1` (top), `claude-opus-5-5` (upper), `claude-sonnet-5-5` (mid), `claude-haiku-5-5` (small); anthropic 1.x, langgraph 1.x, langchain-anthropic 1.x, langchain-core 1.x, mcp 2.x, claude-agent-sdk 0.x (verified 2026-10-08).

## Existing repo
- How to recognise it: `interrupt(` calls, `HumanInTheLoopMiddleware`, `interrupt_before=` on a graph, `can_use_tool=` or `permission_mode=` in Agent SDK options, confirmation prompts in a tool-running loop, allow/deny lists.
- Rule: keep the approval mechanism and the repo's permission policy. The router's always-rule applies: tools with irreversible or external effects (send, delete, pay, deploy) need human approval unless the user or the repo's permission policy says otherwise.

## New repo default
- Classify every tool once, in code next to its definition:
  - read-only: run automatically.
  - write, reversible: follow policy (auto when the policy says so, else ask).
  - irreversible or external (send, delete, pay, deploy): human approval, unless the user or the repo's permission policy says otherwise.
- Approval UX: show the exact action and the exact arguments the tool will run with; offer approve, edit (change arguments) and reject (with a reason the model sees); log who decided what, when, and with which arguments.
- LangGraph: call `interrupt(payload)` inside the tool, or in a node before it. The run pauses and resumes with `Command(resume=value)`; the resume value becomes the return value of `interrupt()`.
- Requirements: a checkpointer (in-memory for dev, a durable one such as `AsyncPostgresSaver` for prod) and a `thread_id` in `config={"configurable": {...}}`; the payload must be JSON-serializable.
- Rules from the docs: never wrap `interrupt()` in bare `try/except` (it works by raising a special exception); the node restarts from its first line on resume, so code before `interrupt()` must be idempotent or moved after it; keep interrupt order stable.
- LangChain's `HumanInTheLoopMiddleware(interrupt_on={...})` for `create_agent` offers decisions `approve`, `edit`, `reject`, `respond`, with the same checkpointer requirement.
- Claude Agent SDK: pass `permission_mode` explicitly (an omitted one may start in `auto`; values `default`, `dontAsk`, `acceptEdits`, `bypassPermissions`, `plan`, `auto`) and pass `can_use_tool=` to `ClaudeAgentOptions`; the callback returns `PermissionResultAllow(updated_input=...)` or `PermissionResultDeny(message=...)`. In Python the docs mark as required: a streaming-input prompt (async generator yielding `{"type": "user", "message": {...}}`, not a plain string) plus a pass-through hook, `hooks={"PreToolUse": [HookMatcher(matcher=None, hooks=[dummy_hook])]}` where `dummy_hook` returns `{"continue_": True}`, to keep the stream open. It never fires for tools approved earlier by rules or a mode, so put checks that must run on every call in a `PreToolUse` hook.

```python
from langchain_core.tools import tool
from langgraph.types import Command, interrupt

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email to an external recipient. Irreversible; needs human approval."""
    decision = interrupt({"action": "send_email",
                          "args": {"to": to, "subject": subject, "body": body}})
    if decision.get("type") not in ("approve", "edit"):  # fail closed on anything else
        return f"Not approved: {decision.get('reason', 'no reason given')}. Do not retry unchanged."
    args = decision.get("args") or {"to": to, "subject": subject, "body": body}  # edited args win
    audit_log(decision, args)   # your logger: who, when, what
    deliver(**args)             # side effect only after approval; your sender
    return "Email sent."

# graph: StateGraph(...).compile(checkpointer=checkpointer), with send_email in a ToolNode
cfg = {"configurable": {"thread_id": "support-42"}}
# graph.invoke(inputs, cfg) pauses at interrupt(); show the payload to the human, then:
# graph.invoke(Command(resume={"type": "approve"}), cfg)
# graph.invoke(Command(resume={"type": "approve", "args": {...edited...}}), cfg)
# graph.invoke(Command(resume={"type": "reject", "reason": "wrong recipient"}), cfg)
```

## Avoid
- Approving by tool name only → the human cannot judge → show the exact arguments.
- Side effects before `interrupt()` in the same node → they repeat on resume → perform them after approval.
- `try/except Exception` around `interrupt()` → swallows the pause → let it propagate.
- No `thread_id` or checkpointer → cannot resume → pass both.
- `bypassPermissions` or broad `allowed_tools` in an agent that touches real systems → every tool runs unprompted → `default` or `dontAsk` plus explicit rules.
- `can_use_tool` with a plain string prompt and no `PreToolUse` hook → the callback is not reached → streaming prompt plus the pass-through hook.
- Asking approval for every read → approval fatigue → classify and auto-run read-only tools.

## Sources
- https://docs.langchain.com/oss/python/langgraph/interrupts (fetched 2026-10-08)
- https://docs.langchain.com/oss/python/langchain/human-in-the-loop (fetched 2026-10-08)
- https://code.claude.com/docs/en/agent-sdk/permissions (fetched 2026-10-08; redirected from docs.claude.com/en/api/agent-sdk/permissions via platform.claude.com)
- https://code.claude.com/docs/en/agent-sdk/user-input (fetched 2026-10-08; linked from the permissions page, source of the Python `can_use_tool` form)
- https://www.anthropic.com/engineering/building-effective-agents (fetched 2026-10-08)
