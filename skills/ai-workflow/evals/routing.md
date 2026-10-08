# AI workflow routing evals

Each prompt assumes the `ai-workflow` skill is loaded. Pass = agent opens every `expect` file, none of the `must-not` files, and shows `behavior` when given. Unless the prompt says otherwise, assume the repo already has .claude/conventions/ai-workflow.md.

## E01
prompt: Start a new project in this empty folder: an assistant that answers questions about our product.
expect: choose-conventions.md
must-not: detect-conventions.md

## E02
prompt: Repo has pyproject.toml listing anthropic and langgraph but no .claude/conventions/ai-workflow.md. Add a node that summarises the ticket text.
expect: detect-conventions.md, langgraph-basics.md
must-not: choose-conventions.md

## E03
prompt: Should our ticket-triage feature be one prompt, a fixed chain of steps, or an autonomous agent?
expect: agent-patterns.md
must-not: langgraph-agents.md

## E04
prompt: Build the file-cleanup agent with the Claude Agent SDK and give it read-only file access.
expect: claude-agent-sdk.md
must-not: langgraph-basics.md

## E05
prompt: Our nightly job classifies 50,000 tickets and is too expensive; cut the cost without losing much quality.
expect: models-and-cost.md
must-not: langgraph-testing.md

## E06
prompt: Rewrite our system prompt so the model stops ignoring the required answer format.
expect: prompting.md
must-not: langgraph-testing.md

## E07
prompt: Our support chat fails with a context-length error after about 200 turns; keep long chats working.
expect: context-engineering.md
must-not: langgraph-testing.md

## E08
prompt: The assistant should remember each user's preferred language across sessions.
expect: memory.md
must-not: langgraph-persistence.md

## E09
prompt: Answer questions from our 2,000 PDF manuals and cite the page each answer came from.
expect: rag.md
must-not: langgraph-testing.md

## E10
prompt: Every request resends the same 30k-token policy document; reduce cost and latency.
expect: prompt-caching.md
must-not: langgraph-testing.md

## E11
prompt: Define a search_orders tool for the model; it keeps passing dates in the wrong format.
expect: tool-design.md
must-not: langgraph-testing.md

## E12
prompt: We expose 120 tools from 8 services and the model often calls the wrong one.
expect: tool-selection.md
must-not: langgraph-testing.md

## E13
prompt: Make the model always return sentiment and confidence as valid JSON matching our schema.
expect: structured-outputs-and-thinking.md
must-not: langchain-models.md

## E14
prompt: A web page the bot fetched contained hidden instructions and the bot followed them; stop that.
expect: guardrails.md
must-not: langgraph-testing.md

## E15
prompt: Before the agent sends any email or deletes a record, a person must approve it.
expect: permissions-and-approval.md
must-not: langgraph-agents.md

## E16
prompt: Expose our inventory database to Claude as an MCP server with a lookup tool.
expect: mcp-servers.md
must-not: mcp-clients.md

## E17
prompt: Let our agent use the tools from the company's existing MCP server.
expect: mcp-clients.md
must-not: mcp-servers.md

## E18
prompt: Write an Agent Skill that teaches Claude our release checklist.
expect: agent-skills.md
must-not: mcp-servers.md

## E19
prompt: Prove the new prompt is better than the old one before we ship it.
expect: evals.md
must-not: observability.md

## E20
prompt: We can't tell why the agent took 14 steps on one request; record what happens at each step.
expect: observability.md
must-not: evals.md

## E21
prompt: Build a LangGraph graph that classifies a ticket and then routes it to a billing node or a tech node.
expect: langgraph-basics.md
must-not: langgraph-testing.md

## E22
prompt: Make our LangGraph chat continue the same conversation after a server restart.
expect: langgraph-persistence.md
must-not: langgraph-testing.md

## E23
prompt: Turn our LangGraph flow into a supervisor that hands work to a research agent and a writer agent.
expect: langgraph-agents.md
must-not: langgraph-testing.md

## E24
prompt: Stream the graph's tokens to the client as they are produced, and deploy the graph.
expect: langgraph-serving.md
must-not: langgraph-testing.md

## E25
prompt: Our LangChain ChatAnthropic call should return a pydantic object instead of text.
expect: langchain-models.md
must-not: langgraph-testing.md

## E26
prompt: Write unit tests for the LangGraph router node without calling the real model.
expect: langgraph-testing.md
must-not: mcp-servers.md

## E27
prompt: Add a FastAPI CRUD endpoint for products.
expect: none
must-not: detect-conventions.md, choose-conventions.md, langgraph-serving.md
behavior: says plain FastAPI work belongs to the python skill

## E28
prompt: How do I share a pytest fixture across several test modules?
expect: none
must-not: detect-conventions.md, choose-conventions.md, langgraph-testing.md

## E29
prompt: Build a React component that shows a chat bubble.
expect: none
must-not: detect-conventions.md, choose-conventions.md

## E30
prompt: Fine-tune an open-source model on our support tickets.
expect: none
must-not: detect-conventions.md, choose-conventions.md, models-and-cost.md
behavior: says model training/fine-tuning is out of scope for this skill

## E31
prompt: .claude/conventions/ai-workflow.md says "checkpointer: postgres", but the graph I'm editing compiles with InMemorySaver. Add a node that drafts a reply.
expect: none
must-not: detect-conventions.md, choose-conventions.md
behavior: flags the mismatch and asks which wins before writing code

## E32
prompt: .claude/conventions/ai-workflow.md lists "tracing: langfuse". Add tracing to the new summarise node.
expect: observability.md
must-not: detect-conventions.md
behavior: uses Langfuse; does not propose LangSmith

## E33
prompt: Add long-term memory of user preferences to our LangGraph agent.
expect: memory.md, langgraph-persistence.md
must-not: langgraph-testing.md

## E34
prompt: In our LangGraph agent, pause for a human yes/no before the refund tool runs.
expect: permissions-and-approval.md
must-not: langgraph-testing.md

## E35
prompt: Turn on prompt caching for the system prompt of our LangGraph agent that uses ChatAnthropic.
expect: prompt-caching.md, langchain-models.md
must-not: langgraph-testing.md

## E36
prompt: Serve our LangGraph agent from a FastAPI endpoint that streams its output over SSE.
expect: langgraph-serving.md
must-not: choose-conventions.md
behavior: handles the graph streaming part and says FastAPI endpoint details belong to the python skill

## E37
prompt: Block prompt injection that arrives inside retrieved documents in our RAG pipeline.
expect: guardrails.md, rag.md
must-not: langgraph-testing.md

## E38
prompt: Our Python script calls Claude directly and fails when the API is overloaded; add retries and a timeout.
expect: models-and-cost.md
must-not: langgraph-basics.md

## E39
prompt: Call Claude from our Next.js route handler with the TypeScript SDK.
expect: none
must-not: detect-conventions.md, choose-conventions.md, models-and-cost.md
behavior: says Claude code in TypeScript/JavaScript is out of scope for this skill
