# Claude Agent SDK (Python)

> Load when: Claude Agent SDK, `claude_agent_sdk`, `ClaudeSDKClient`, `query()`. Pinned: model IDs `claude-fable-5-1` (top), `claude-opus-5-5` (upper), `claude-sonnet-5-5` (mid), `claude-haiku-5-5` (small); anthropic 1.x, langgraph 1.x, langchain-anthropic 1.x, langchain-core 1.x, mcp 2.x, claude-agent-sdk 0.x (verified 2026-10-08).

## Existing repo
- How to recognise it: `claude-agent-sdk` in dependencies, `from claude_agent_sdk import ...`, `ClaudeAgentOptions(...)`.
- Rule: keep the SDK and its options style; do not port it to LangGraph unasked.

## New repo default
- What it is: Claude Code's tools, agent loop and context management as a library for Python (and TypeScript). It runs the Claude Code binary; the package bundles the CLI (`cli_path` overrides it). Install: `pip install claude-agent-sdk`, Python 3.10 or newer.
- `query(prompt=..., options=...)` creates a new session per call and yields messages as an async iterator. Use it for one-shot tasks.
- `ClaudeSDKClient` is the bidirectional, multi-turn client: `await client.query(...)`, then `client.receive_response()`. Custom tools and hooks as Python functions go through it or `query()`.
- Key `ClaudeAgentOptions` fields: `system_prompt`, `allowed_tools` (auto-approve), `disallowed_tools` (deny), `permission_mode` (`default`, `acceptEdits`, `plan`, `dontAsk`, `bypassPermissions`, `auto`), `cwd`, `mcp_servers`, `hooks`, `max_turns`.
- Custom tools: `@tool(name, description, input_schema)` plus `create_sdk_mcp_server(...)` makes an in-process MCP server; allow it as `mcp__<server key>__<tool name>`.
- Hooks: `hooks={"PreToolUse": [HookMatcher(matcher="Bash", hooks=[fn])]}`; a hook can return a `permissionDecision` of `deny`.
- Authentication: use API-key auth; the docs say third parties may not offer claude.ai login for agents built on the SDK.
- Choose it for: developer or automation agents that need file and shell tools, permissions, sessions, subagents and MCP out of the box.
- Choose LangGraph instead for: an explicit state machine you design node by node, with typed state and your own checkpointer. For a hosted agent without running the loop yourself, the docs list Managed Agents.
- The overview says sessions can be resumed or forked; verify your per-user persistence needs against the sessions page before building a multi-tenant backend on it.

Read-only agent (analysis, no writes):

```python
import anyio
from claude_agent_sdk import ClaudeAgentOptions, AssistantMessage, TextBlock, query

options = ClaudeAgentOptions(
    system_prompt="You review code and report findings. Never modify files.",
    allowed_tools=["Read", "Grep", "Glob"],
    disallowed_tools=["Write", "Edit", "Bash"],
    permission_mode="dontAsk",  # deny any tool not pre-approved in allowed_tools instead of prompting
    cwd="/path/to/project",
    max_turns=10,
)

async def main():
    async for message in query(prompt="List TODOs in src/", options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)

anyio.run(main)
```

## Avoid
- `bypassPermissions` in anything shared or deployed → every tool runs unprompted → list `allowed_tools` and a stricter mode.
- Bash in `allowed_tools` for untrusted input → shell access from prompt injection → read-only tools or a `PreToolUse` hook.
- Forgetting the `mcp__server__tool` name → custom tool is never allowed → build the name from the server key.
- Using it as a web request handler without limits → each run drives a Claude Code process → set `max_turns` and budgets.

## Sources
- https://code.claude.com/docs/en/agent-sdk/overview (fetched 2026-10-08; docs.claude.com redirects here)
- https://code.claude.com/docs/en/agent-sdk/python (fetched 2026-10-08)
- https://github.com/anthropics/claude-agent-sdk-python (fetched 2026-10-08)
- https://claude.com/blog/building-agents-with-the-claude-agent-sdk (fetched 2026-10-08; anthropic.com/engineering redirects here)
- https://pypi.org/project/claude-agent-sdk/ (fetched 2026-10-08)
