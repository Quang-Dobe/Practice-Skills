# Testing

> Load when: writing or running tests (not API tests), pytest, fixtures, parametrize, mocks, coverage. Pinned: Python 3.14, uv 0.12, ruff 0.16, mypy 2.4, pytest 9, pydantic 2.13, FastAPI 0.142, SQLAlchemy 2.1.

## Existing repo
- Recognise it: `tests/` with `test_*.py` or `conftest.py`, `[tool.pytest.ini_options]` in `pyproject.toml`, `pytest.ini`, `tox.ini`, `.coveragerc`; `import unittest` / `TestCase` classes mean unittest.
- Rule: follow what is there. Keep unittest classes and runners when the repo uses them; keep its async mode, markers, fixtures and mock library (`pytest-mock` or plain `unittest.mock`).
- New tests copy the nearest existing test file's layout and naming.

## New repo default
- Layout: `tests/` at the repo root, files `test_*.py`, plain `assert` (no `self.assertEqual`).
- Fixtures: `@pytest.fixture`, default scope is function; widen to `module` or `session` only for costly setup. Shared fixtures live in `conftest.py`, found without imports. Use `yield` for teardown.
- `@pytest.mark.parametrize("a,b", [...])` for table cases; `pytest.param(..., marks=...)` to mark single cases.
- Built-ins: `tmp_path` for files, `monkeypatch` for env vars, attributes and `cwd`.
- Async: `pytest-asyncio`; set `asyncio_mode` in config. Default is `strict` (needs `@pytest.mark.asyncio` and `@pytest_asyncio.fixture`); `auto` marks every async test, which suits asyncio-only projects.
- Coverage: `pytest-cov`; options `--cov=<pkg>`, `--cov-report=term-missing`, `--cov-fail-under=N`, `--cov-branch`.
- Mock only at boundaries (network, clock, filesystem, third-party services); prefer fakes or real objects for your own code.

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = "--cov=my_pkg --cov-report=term-missing --cov-branch"
```

```python
import pytest


@pytest.fixture
def settings_file(tmp_path):
    path = tmp_path / "settings.toml"
    path.write_text("debug = true\n")
    return path


@pytest.mark.parametrize("raw,expected", [("1", 1), ("42", 42), pytest.param("x", None, id="bad")])
def test_parse(raw, expected):
    from my_pkg.parse import parse_int  # returns None on bad input

    assert parse_int(raw) == expected


def test_env(monkeypatch):
    monkeypatch.setenv("APP_ENV", "test")


@pytest.mark.asyncio  # redundant in auto mode, required in strict mode
async def test_fetch():
    async def fake_get(path: str) -> str:
        return "pong"

    assert await fake_get("/ping") == "pong"
```

## Avoid
- Patching your own internals (`mock.patch("my_pkg.a.b")` everywhere) → tests break on refactor and prove nothing → fake the boundary object or pass it in.
- Mixing unittest `TestCase` into an async-pytest suite → standard unittest test classes are not compatible with pytest-asyncio → use `unittest.IsolatedAsyncioTestCase` or plain async functions.
- Wide-scope fixtures that hold mutable state → tests leak into each other → function scope, or reset in teardown.
- Real network, clock or `.env` reads in unit tests → flaky and slow → inject or monkeypatch.

## Sources
- https://docs.pytest.org/en/stable/how-to/fixtures.html (fetched 2026-10-08)
- https://docs.pytest.org/en/stable/how-to/parametrize.html (fetched 2026-10-08)
- https://pytest-asyncio.readthedocs.io/ (fetched 2026-10-08)
- https://pytest-asyncio.readthedocs.io/en/stable/reference/configuration.html (fetched 2026-10-08)
- https://pytest-asyncio.readthedocs.io/en/stable/concepts.html (fetched 2026-10-08)
- https://pytest-cov.readthedocs.io/ (fetched 2026-10-08)
- https://pytest-cov.readthedocs.io/en/latest/config.html (fetched 2026-10-08)
