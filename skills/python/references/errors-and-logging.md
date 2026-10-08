# Errors and Logging

> Load when: exceptions, error handling, custom errors, logging, structlog. Pinned: Python 3.14, uv 0.12, ruff 0.16, mypy 2.4, pytest 9, pydantic 2.13, FastAPI 0.142, SQLAlchemy 2.1.

## Existing repo
- How to recognise it: an `errors.py` / `exceptions.py` module, `logging.config.dictConfig` or `logging.basicConfig` at the entry point, `import structlog`, loguru imports.
- Rule: follow what is there. Reuse the repo's base exception and logger setup; do not swap logging libraries unasked.
- structlog present → use `structlog.get_logger()` everywhere, not stdlib calls mixed in.

## New repo default
- One small hierarchy per package: `class AppError(Exception)` as the base, specific subclasses below it. Derive from `Exception`, never `BaseException`; inherit from one built-in at most. Names end in `Error`.
- Catch the narrowest type you can handle. Re-raise or translate at layer boundaries with `raise DomainError(...) from err` (`from None` only to hide noise on purpose). `err.add_note("...")` adds context without wrapping.
- `TaskGroup` and similar raise `ExceptionGroup`: handle with `except* SomeError`.
- Logging: `logger = logging.getLogger(__name__)` in every module; configure once at the entry point with `logging.config.dictConfig`; libraries add nothing but a `NullHandler`.
- Use lazy formatting, `logger.info("user %s done", user_id)`, and `logger.exception("...")` inside `except` blocks to log the traceback.
- structlog (only when the repo has it): `structlog.get_logger().bind(request_id=...)` for context, `structlog.contextvars.bind_contextvars(...)` for per-request context, `JSONRenderer` for JSON output.

```python
import logging
import logging.config

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base class for this package's errors."""


class ConfigError(AppError):
    pass


def load_port(raw: str) -> int:
    try:
        return int(raw)
    except ValueError as err:
        raise ConfigError(f"bad port: {raw!r}") from err


def setup_logging() -> None:  # call once, from the entry point
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {"std": {"format": "%(asctime)s %(levelname)s %(name)s %(message)s"}},
        "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "std"}},
        "root": {"level": "INFO", "handlers": ["console"]},
    })


def main() -> None:
    setup_logging()
    try:
        port = load_port("80a")
    except ConfigError:
        logger.exception("startup failed")
        raise SystemExit(1) from None
    logger.info("listening on %s", port)
```

## Avoid
- Bare `except:` or `except Exception: pass` → swallows bugs silently → catch the narrowest type; log or re-raise.
- `raise NewError(...)` inside `except` without `from` → the cause link is only implicit → `raise NewError(...) from err`.
- Catching and re-raising at every layer → duplicate logs → translate once at a boundary and log once.
- f-strings in log calls (`logger.info(f"...")`) → formatting cost even when the level is off → `%s` arguments.
- `logging.basicConfig` or handlers in library code → takes configuration away from the application → entry point only; libraries use `NullHandler`.
- `logger.error(str(e))` in a handler → loses the traceback → `logger.exception(...)`.
- Multiple built-in bases (`class E(ValueError, TypeError)`) → memory-layout conflicts → one base.

## Sources
- https://docs.python.org/3/tutorial/errors.html (fetched 2026-10-08)
- https://docs.python.org/3/library/exceptions.html (fetched 2026-10-08)
- https://docs.python.org/3/howto/logging.html (fetched 2026-10-08)
- https://www.structlog.org/ and https://www.structlog.org/en/stable/getting-started.html (fetched 2026-10-08)
