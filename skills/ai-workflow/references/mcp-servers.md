# MCP servers (Python)

> Load when: building an MCP server, exposing tools/resources/prompts over MCP, FastMCP. Pinned: model IDs `claude-fable-5-1` (top), `claude-opus-5-5` (upper), `claude-sonnet-5-5` (mid), `claude-haiku-5-5` (small); anthropic 1.x, langgraph 1.x, langchain-anthropic 1.x, langchain-core 1.x, mcp 2.x, claude-agent-sdk 0.x (verified 2026-10-08).

## Existing repo
- How to recognise it: `mcp` in dependencies; `from mcp.server import MCPServer` (2.x) or an older `FastMCP` import from the 1.x SDK; `@mcp.tool()` / `@mcp.resource()` / `@mcp.prompt()` decorators; `mcp.run(...)` or `mcp dev` in scripts.
- Rule: follow what is there (class, transport, auth). Check the installed `mcp` major version before copying snippets; the SDK publishes a 1.x to 2.x migration guide.
- Keep the repo's tool naming and error style; the tool design rules (names, descriptions, schemas, errors) still apply.

## New repo default
- Official SDK: `pip install "mcp[cli]"`, `from mcp.server import MCPServer` (the 2.x docs show this class; the current pages do not show `FastMCP`).
- Pick the primitive by who controls it: tool = the model calls it (actions, queries); resource = the app reads file-like data by URI; prompt = a template the user picks.
- Type-hinted parameters become the input schema; the docstring becomes the description; `Args:` lines document parameters.
- Transport: `streamable-http` for anything deployed (default here); `stdio` (the `run()` default) only for local servers a host launches.
- SSE is the older HTTP transport: the SDK keeps it for old clients and says not to build new on it; the current spec page lists only stdio and Streamable HTTP.
- stdio: stdout is the wire. Log with `logging` (stderr), never `print()`.
- Remote auth: the server is an OAuth 2.1 resource server (Protected Resource Metadata, bearer token checked on every request, token must be issued for this server, 401/403 with `WWW-Authenticate`). stdio servers take credentials from the environment instead. The SDK has a `TokenVerifier` hook for the check.
- Least privilege: narrow scopes per capability, read-only tools apart from write tools, no tool that takes raw shell or SQL.
- Test with MCP Inspector (`uv run mcp dev server.py` for stdio; `npx @modelcontextprotocol/inspector --server-url <url> --transport http` for remote) and with the SDK `Client` in-memory in pytest.

```python
from mcp.server import MCPServer

mcp = MCPServer("Bookshop")


@mcp.tool()
def search_books(query: str, limit: int = 5) -> str:
    """Search the catalog by title or author.

    Args:
        query: Title or author fragment.
        limit: Maximum results to return.
    """
    return f"Found {limit} books matching {query!r}."


@mcp.resource("book://{isbn}")
def book(isbn: str) -> str:
    """Catalog record for one ISBN."""
    return f"Record for {isbn}"


@mcp.prompt()
def recommend(genre: str) -> str:
    """Ask for reading recommendations."""
    return f"Recommend three {genre} books."


if __name__ == "__main__":
    mcp.run(transport="streamable-http", port=3001)
```

## Avoid
- `print()` in a stdio server → corrupts JSON-RPC on stdout → use `logging` (stderr).
- New servers on SSE → superseded by Streamable HTTP → `transport="streamable-http"`.
- Transport options on `MCPServer(...)` → they belong to `run()` → pass `host`/`port`/`streamable_http_path` there.
- Accepting tokens issued for another server, or passing the client's token downstream → confused-deputy risk; the spec forbids both → validate audience, use separate downstream credentials.
- A local Streamable HTTP server bound to 0.0.0.0, or no `Origin` check → web pages can reach it via DNS rebinding; the spec says servers MUST validate `Origin` (403 if invalid) and SHOULD bind to 127.0.0.1 when local → keep the 127.0.0.1 default locally and validate `Origin` when exposed.
- Broad all-powers tools, secrets in tool arguments → one leaked token or injected prompt gets everything → narrow scopes, secrets from the environment.

## Sources
- https://modelcontextprotocol.io/docs/develop/build-server (fetched 2026-10-08)
- https://github.com/modelcontextprotocol/python-sdk (fetched 2026-10-08); SDK docs https://py.sdk.modelcontextprotocol.io/run/index.md, https://py.sdk.modelcontextprotocol.io/servers/prompts/index.md, https://py.sdk.modelcontextprotocol.io/run/authorization/index.md, https://py.sdk.modelcontextprotocol.io/get-started/testing/index.md (fetched 2026-10-08)
- https://modelcontextprotocol.io/specification/latest/basic/transports (resolves to spec 2026-07-28; fetched 2026-10-08)
- https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http (fetched 2026-10-08)
- https://modelcontextprotocol.io/specification/latest/basic/authorization (spec 2026-07-28; fetched 2026-10-08)
- https://modelcontextprotocol.io/docs/tools/inspector (fetched 2026-10-08)
