# Agent Skills

> Load when: writing Agent Skills, `SKILL.md`, skill references. Pinned: model IDs `claude-fable-5-1` (top), `claude-opus-5-5` (upper), `claude-sonnet-5-5` (mid), `claude-haiku-5-5` (small); anthropic 1.x, langgraph 1.x, langchain-anthropic 1.x, langchain-core 1.x, mcp 2.x, claude-agent-sdk 0.x (verified 2026-10-08).

## Existing repo
- How to recognise it: folders holding `SKILL.md` with YAML frontmatter, under `.claude/skills/`, `~/.claude/skills/`, a plugin, or a zip uploaded to the Skills API.
- Rule: follow the repo's naming style, folder layout and validation scripts; edit skills in place and do not restructure them unasked.
- Custom skills do not sync across surfaces (claude.ai, API, Claude Code are separate); update each place the skill lives.

## New repo default
- A skill is a folder with `SKILL.md` (required YAML `name`, `description`) plus optional reference files and scripts.
- `name`: max 64 chars, lowercase letters, digits, hyphens; no XML tags; no "anthropic" or "claude". `description`: non-empty, max 1,024 chars, no XML tags.
- Progressive disclosure: metadata always in the system prompt, SKILL.md body read when triggered, other files read or run only when needed. Script code never enters context, only its output.
- Description says what the skill does AND when to use it, in third person ("Processes Excel files..."), with trigger terms. Not "I can help" or "You can use".
- Keep the SKILL.md body under 500 lines; move detail into files linked directly from SKILL.md (one level deep, never reference to reference). A reference over 100 lines starts with a table of contents.
- Be concise: add only what Claude does not already know. Match freedom to fragility: exact scripts for fragile steps, prose for judgment calls.
- Put deterministic steps in scripts that handle their own errors; say whether Claude runs a script or reads it. Forward slashes in all paths.
- Evaluate first: run representative tasks without the skill, write at least three evaluations, add minimal instructions, compare to the baseline; test with the models you will use (small, mid, top).
- Where skills run: Claude Code (filesystem, full network), claude.ai (zip upload, plan-dependent), Claude API (`container` with `skill_id` plus the code execution tool; no network, no runtime package installs).
- Skills vs MCP: a skill carries know-how and procedure; MCP connects tools and data. Often both: the skill says when and how to use the server's tools, by qualified name `Server:tool`.
- Use skills only from trusted sources; audit bundled scripts and external fetches.

```markdown
---
name: processing-invoices
description: Extracts line items from invoice PDFs and validates totals. Use when the user mentions invoices, PDF billing documents, or totals that do not add up.
---

# Processing invoices

Run `python scripts/extract.py input.pdf > items.json`, then `python scripts/validate.py items.json`.
If validation fails, fix `items.json` and rerun. Edge cases: see [EDGE-CASES.md](EDGE-CASES.md).
```

## Avoid
- Vague or first-person description ("Helps with documents") → the skill never triggers or collides → state what + when, third person, key terms.
- Over-explaining what Claude knows → every loaded token competes with the conversation → cut it.
- Nested references (file A links file B) → Claude may preview with `head` and miss content → link everything from SKILL.md.
- Time-sensitive instructions ("before August 2025") → silently goes stale → a current section plus an "old patterns" section.
- Listing many options → indecision → give a default plus one escape hatch.
- Long skill without evals → documents imagined problems → evaluations first.

## Sources
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview (redirected from docs.claude.com; fetched 2026-10-08)
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices (redirected from docs.claude.com; fetched 2026-10-08)
- https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills (fetched 2026-10-08)
- https://github.com/anthropics/skills (fetched 2026-10-08)
