# MCP clients (Python)

> Load when: connecting an app or agent to an existing MCP server, MCP client, MCP connector, `langchain-mcp-adapters`, `langchain[mcp]` / `MCPAdapter`. Pinned: model IDs `claude-fable-5-1` (top), `claude-opus-5-5` (upper), `claude-sonnet-5-5` (mid), `claude-haiku-5-5` (small); anthropic 1.x, langgraph 1.x, langchain-anthropic 1.x, langchain-core 1.x, mcp 2.x, claude-agent-sdk 0.x (verified 2026-10-08).

## Existing repo
- How to recognise it: `mcp_servers=` with `betas=[...]` in `client.beta.messages.create` (API connector); `from mcp import Client` or `ClientSession` (SDK client); `langchain_mcp_adapters` with `MultiServerMCPClient`, or `from langchain.mcp import MCPAdapter`.
- Rule: follow what is there. LangChain docs now say MCP ships inside `langchain[mcp]>=1.4.0` (beta) and replaces `langchain-mcp-adapters`; do not migrate unasked.
- Keep the repo's server allowlist and token handling.

## New repo default
Choose by where the loop runs:

| Option | Use when | Limits (per docs) |
|---|---|---|
| API MCP connector | Anthropic SDK workflow, server on public HTTPS | tool calls only; no local stdio; beta header `mcp-client-2025-11-20` |
| SDK `Client` + own loop | stdio, resources, or full control | you map tools and run the loop |
| LangChain `MCPAdapter` | LangGraph / `create_agent` agent | beta; prompts and resources not supported |

- Connector: every server in `mcp_servers` needs exactly one `mcp_toolset` in `tools`. Allowlist with `default_config` `enabled: false` plus per-tool `configs`, or denylist write tools.
- Treat MCP tool output as untrusted data, never instructions. Expose only the servers and tools the task needs.
- Many MCP tools cost context on every call; the tool selection reference has the remedies.
- Code execution with MCP (the agent writes code against tool APIs and filters data in a sandbox) cuts context use; Anthropic's post reports 150,000 to 2,000 tokens in its example and names sandboxing and monitoring as the cost.

```python
from anthropic import AsyncAnthropic
from mcp import Client
from mcp_types import TextContent

MODEL = "claude-sonnet-5-5"  # from settings in real code
anthropic = AsyncAnthropic()
async def ask(url: str, question: str) -> str:
    async with Client(url) as mcp:  # a URL means Streamable HTTP
        listed = await mcp.list_tools()
        tools = [
            {"name": t.name, "description": t.description, "input_schema": t.input_schema}
            for t in listed.tools
        ]
        messages = [{"role": "user", "content": question}]
        for _ in range(10):  # iteration cap
            resp = await anthropic.messages.create(
                model=MODEL, max_tokens=1000, messages=messages, tools=tools
            )
            calls = [b for b in resp.content if b.type == "tool_use"]
            if not calls:
                return "".join(b.text for b in resp.content if b.type == "text")
            messages.append({"role": "assistant", "content": resp.content})
            results = []
            for c in calls:  # approval gate for write tools goes here
                r = await mcp.call_tool(c.name, c.input)
                text = "\n".join(b.text for b in r.content if isinstance(b, TextContent))
                results.append({"type": "tool_result", "tool_use_id": c.id,
                                "content": text, "is_error": r.is_error})
            messages.append({"role": "user", "content": results})
        raise RuntimeError("tool loop hit the iteration cap")
```

Connector call: `client.beta.messages.create(..., mcp_servers=[{"type": "url", "url": "https://...", "name": "x", "authorization_token": TOKEN}], tools=[{"type": "mcp_toolset", "mcp_server_name": "x"}], betas=["mcp-client-2025-11-20"])`. LangChain: `async with MCPAdapter("https://.../mcp") as a: tools = await a.list_tools()`, then pass `tools` to `create_agent`.

## Avoid
- Feeding MCP results back as instructions → tool output can carry injection → pass as tool results, screen them, keep approval on writes.
- Connecting every available server → context cost and wrong-tool picks → allowlist per task.
- Pointing the connector at a local stdio server → not supported → use the SDK client, or serve the MCP server over HTTPS.
- A file-path string given to `MCPAdapter` → docs reject non-URL strings so config or model text cannot launch a process → `Path` for scripts, `str` only for http(s) URLs.
- A hard-coded `authorization_token` → leaks → read it from the environment or a secret store.

## Sources
- https://platform.claude.com/docs/en/agents-and-tools/mcp-connector (redirected from docs.claude.com; fetched 2026-10-08)
- https://modelcontextprotocol.io/docs/develop/build-client (fetched 2026-10-08); https://py.sdk.modelcontextprotocol.io/client/transports/index.md (fetched 2026-10-08)
- https://docs.langchain.com/oss/python/langchain/mcp and https://docs.langchain.com/oss/python/migrate/langchain-mcp-adapters (fetched 2026-10-08)
- https://www.anthropic.com/engineering/code-execution-with-mcp (fetched 2026-10-08)
