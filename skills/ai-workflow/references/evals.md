# Evals

> Load when: measuring output quality, comparing prompts or models, eval datasets, graders. Pinned: model IDs `claude-fable-5-1` (top), `claude-opus-5-5` (upper), `claude-sonnet-5-5` (mid), `claude-haiku-5-5` (small); anthropic 1.x, langgraph 1.x, langchain-anthropic 1.x, langchain-core 1.x, mcp 2.x, claude-agent-sdk 0.x (verified 2026-10-08).

## Existing repo
- How to recognise it: an `evals/` or `tests/evals/` folder, JSONL/YAML datasets, grader functions, `@pytest.mark.langsmith`, `langsmith` `evaluate(...)`, or a CI job that runs them.
- Rule: follow what is there (runner, dataset format, graders) and add cases to the existing dataset; never swap eval frameworks unasked.
- The always-rule applies: every prompt or model change ships with an eval run.

## New repo default
- Write success criteria first: specific and measurable, e.g. "F1 >= 0.85 on a held-out set", across task fidelity, consistency, latency and cost, not accuracy alone.
- Dataset: real cases (bugs, support tickets, logs) plus edge cases (missing or irrelevant input, very long input, harmful or ambiguous input). Start with 20-50 tasks; version the file in the repo.
- Prefer volume with automated grading over a few hand-graded cases.
- Graders: code-based first (exact match, regex, JSON schema, tool-call checks); LLM-as-judge with a clear rubric for tone or open-ended quality; human review to calibrate the judge.
- LLM judge rules: use a different model than the one under test, structured verdict (number or label), reasoning before the verdict, test the judge on known cases. Spot-check the judge against human labels.
- Agents: grade the outcome (final state, files, DB rows), not the exact tool path; read transcripts of failures to check the graders themselves.
- Non-determinism: run several trials per task; pass@k = at least one success in k, pass^k = all k succeed. Pick by whether one success or consistency matters.
- Capability evals start low and measure headroom; regression evals should stay near 100%.
- Run as a pytest suite in CI on prompt, tool or model changes. Compare with the stored baseline; record cost, tokens and latency per run.
- Repo already on LangSmith: use its datasets, evaluators and experiments instead; `@pytest.mark.langsmith` (install `langsmith[pytest]`) logs pytest cases as an experiment.

```python
import json
import pathlib

import pytest

CASES = [json.loads(l) for l in pathlib.Path("evals/triage.jsonl").read_text().splitlines()]
BASELINE = 0.90  # recorded from the last accepted run


def run_app(text: str) -> str:
    raise NotImplementedError  # call the real prompt/graph here


def grade(output: str, case: dict) -> bool:
    return output.strip().lower() == case["expected"]  # code grader


def test_triage_accuracy():
    passed = sum(grade(run_app(c["input"]), c) for c in CASES)
    assert passed / len(CASES) >= BASELINE
```

## Avoid
- "Looks good" checks → no regression signal → numeric criteria and a stored baseline.
- Only happy-path cases → production edge cases fail unseen → add edge and failure cases from real traffic.
- Same model grading its own output → bias → separate judge model, calibrated against human labels.
- Asserting an exact tool sequence for agents → brittle, rejects valid paths → grade the outcome.
- Hitting the live API on every local test run → cost and flakiness → run the suite in CI and on prompt/model changes.

## Sources
- https://platform.claude.com/docs/en/test-and-evaluate/define-success (redirected from docs.claude.com; fetched 2026-10-08)
- https://platform.claude.com/docs/en/test-and-evaluate/develop-tests (redirected from docs.claude.com; fetched 2026-10-08)
- https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents (fetched 2026-10-08)
- https://docs.langchain.com/langsmith/evaluation (fetched 2026-10-08); https://docs.langchain.com/langsmith/pytest (fetched 2026-10-08)
