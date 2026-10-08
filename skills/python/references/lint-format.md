# Lint and Format

> Load when: ruff, black, flake8, isort, lint/format config, pre-commit hooks. Pinned: Python 3.14, uv 0.12, ruff 0.16, mypy 2.4, pytest 9, pydantic 2.13, FastAPI 0.142, SQLAlchemy 2.1.

## Existing repo
- How to recognise it: `[tool.ruff]` or `ruff.toml` → ruff; `[tool.black]`, `.flake8`, `[tool.isort]`, a flake8 section in `setup.cfg` → black + flake8 + isort; `.pre-commit-config.yaml` lists the hooks actually enforced.
- Rule: follow what is there. Keep black + flake8 + isort when present; do not migrate to ruff unasked. Keep the existing line length and rule selection.

## New repo default
- ruff does both jobs: `ruff check --fix` (lint) and `ruff format` (format). Configure in `pyproject.toml` under `[tool.ruff]`; lint options go under `[tool.ruff.lint]`.
- Starter rule set: `E` (pycodestyle errors), `F` (Pyflakes), `I` (isort ordering), `B` (bugbear), `UP` (pyupgrade), `SIM` (simplify). Add more only when asked.
- Set `target-version` to match `requires-python`; `line-length` defaults to 88.
- Run through uv: `uv add --dev ruff`, then `uv run ruff check --fix .` and `uv run ruff format .`.
- pre-commit: ruff hooks plus the type checker; in CI run `ruff check` and `ruff format --check`.

```toml
[tool.ruff]
line-length = 88
target-version = "py314"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "SIM"]

[tool.ruff.format]
quote-style = "double"
```

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.16.10
    hooks:
      - id: ruff-check
        args: [--fix]
      - id: ruff-format
  - repo: local
    hooks:
      - id: mypy
        name: mypy
        entry: uv run mypy src
        language: unsupported
        types: [python]
        pass_filenames: false
```

Then `uv run pre-commit install` once and `uv run pre-commit run --all-files` to check.

## Avoid
- ruff and black/isort together on one codebase → competing formatting → one formatter.
- `ruff-format` before `ruff-check --fix` in pre-commit → fixes can leave code unformatted → lint hook first, then format (the ruff docs ask for this order).
- `select = ["ALL"]` on an existing repo → floods the diff with unrelated findings → extend the current selection one prefix at a time.
- Blanket `# noqa` → hides real findings → `# noqa: CODE` with the specific rule.
- A pre-commit `rev` copied from memory → stale hooks → take it from the ruff integrations page or run `pre-commit autoupdate`.

## Sources
- https://docs.astral.sh/ruff/configuration/ (fetched 2026-10-08)
- https://docs.astral.sh/ruff/rules/ (fetched 2026-10-08; E, F, I, B, UP, SIM prefixes confirmed)
- https://docs.astral.sh/ruff/integrations/ (fetched 2026-10-08; hook id is `ruff-check`, not the older `ruff`)
- https://pre-commit.com/ (fetched 2026-10-08; local hooks use `language: unsupported`)
