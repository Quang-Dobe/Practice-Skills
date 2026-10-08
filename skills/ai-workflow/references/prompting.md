# Prompting

> Load when: writing or reviewing prompts, system prompts, few-shot examples or output-format instructions. Pinned: model IDs `claude-fable-5-1` (top), `claude-opus-5-5` (upper), `claude-sonnet-5-5` (mid), `claude-haiku-5-5` (small); anthropic 1.x, langgraph 1.x, langchain-anthropic 1.x, langchain-core 1.x, mcp 2.x, claude-agent-sdk 0.x (verified 2026-10-08).

## Existing repo
- How to recognise it: prompts live as module constants, `.txt`/`.md`/`.jinja` files, a `prompts/` folder, or LangChain `ChatPromptTemplate` objects; system text passed as `system=` to `messages.create`.
- Rule: follow the existing storage and templating style; improve the prompt text, do not move prompts to a new mechanism unasked.
- Prompts that end with a prefilled assistant turn break on the pinned models (see Avoid); that is a fix, not a migration.

## New repo default
- Be clear and direct: state the task, output format and constraints. Test: would a colleague with no context be confused? Then Claude will be too.
- Give the why. "Read aloud by a text-to-speech engine, so never use ellipses" generalizes better than "NEVER use ellipses".
- Set a role in the system prompt; one sentence is enough.
- Separate instructions, context, examples and variable input with consistent, descriptive XML tags (`<instructions>`, `<context>`, `<input>`); nest tags for hierarchy.
- Few-shot: examples that are relevant, diverse (edge cases) and wrapped in `<example>` inside `<examples>`; the docs recommend 3-5.
- Long documents (20k+ tokens) go at the top, query and instructions last; wrap each in `<document>` with `<source>` and `<document_content>` subtags. The docs report queries at the end can improve quality by up to 30 percent in tests.
- Format control: say what to do instead of what not to do; match the prompt's own style to the desired output (a markdown-free prompt gives less markdown); or ask for output inside a named tag.
- Keep prompts in versioned files or constants and gate every change with an eval run.

```python
SYSTEM = "You are a support-ticket triager for a billing product."  # one-line role

def build_user_prompt(policy: str, examples: list[str], ticket: str) -> str:
    shots = "\n".join(f"<example>\n{e}\n</example>" for e in examples)
    return (
        f"<policy>\n{policy}\n</policy>\n"  # long data first
        f"<examples>\n{shots}\n</examples>\n"
        f"<ticket>\n{ticket}\n</ticket>\n\n"  # query last
        "Classify the ticket as billing, bug or other. "
        "Your answer is one lowercase word inside <label> tags, "
        "because a parser reads it."
    )

resp = client.messages.create(
    model=settings.MODEL_MID, max_tokens=1024,  # from app settings; thinking shares this budget
    system=SYSTEM,
    messages=[{"role": "user", "content": build_user_prompt(p, ex, t)}],
)
```

## Avoid
- Prefilling the last assistant turn → no longer supported starting with Claude 4.6 models, so the pinned models reject that pattern → use direct instructions, XML output tags, structured outputs or tool calling; strip stray preambles in post-processing.
- "Do not use markdown" style negations → weaker than a positive description → write "smoothly flowing prose paragraphs".
- Bare ALL-CAPS rules with no reason → the model cannot generalize → add the why.
- One-shot or look-alike examples → the model copies unintended patterns → vary them and cover edge cases.
- Query before a long document → worse recall on long inputs → documents first, query last.
- Prompt edits shipped without an eval run → silent regressions → run the eval suite.

## Sources
- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview (fetched 2026-10-08; redirected from docs.claude.com; points to the best-practices page below)
- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices (fetched 2026-10-08; the docs.claude.com claude-4-best-practices, use-xml-tags and multishot-prompting URLs all redirect here)
