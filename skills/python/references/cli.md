# CLI

> Load when: command-line tools, subcommands, options, Typer, argparse, Click. Pinned: Python 3.14, uv 0.12, ruff 0.16, mypy 2.4, pytest 9, pydantic 2.13, FastAPI 0.142, SQLAlchemy 2.1.

## Existing repo
- Recognise it: `import argparse` with `ArgumentParser`, `import click` with `@click.command`, `import typer`, `[project.scripts]` or `console_scripts` entries, a `__main__.py`.
- Rule: follow what is there. Keep argparse or Click; never convert to Typer unasked. Extend the existing parser, group or sub-app in the same style.

## New repo default
- Typer: `app = typer.Typer()`, commands with `@app.command()`, type-hinted parameters; options as `Annotated[type, typer.Option()]`.
- Subcommand groups: one `typer.Typer()` per module, joined with `app.add_typer(users.app, name="users")`.
- Exit codes: `raise typer.Exit(code=1)` for failure (0 = success); `typer.Abort()` also exits and prints "Aborted!".
- Keep command bodies thin: parse arguments, call library functions, map errors to exit codes.
- Entry point in `[project.scripts]` pointing at the `Typer` object; install with `uv sync`. An installed package is also what makes shell completion work.
- argparse (stdlib, no dependency): `add_subparsers(required=True, dest=...)`, `set_defaults(func=...)`, and `sys.exit(main())` where `main` returns the code.

```toml
[project.scripts]
my-tool = "my_pkg.cli:app"
```

```python
from typing import Annotated

import typer

app = typer.Typer()
users = typer.Typer()
app.add_typer(users, name="users")


@users.command()
def create(
    name: str,
    admin: Annotated[bool, typer.Option("--admin/--no-admin", help="Grant admin")] = False,
) -> None:
    """Create a user."""
    if not name.strip():
        typer.echo("name must not be empty", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"created {name} (admin={admin})")


if __name__ == "__main__":
    app()
```

## Avoid
- `sys.exit` / `print` scattered through library code → untestable → raise exceptions, convert them in the command.
- Business logic inside command functions → cannot reuse or test without the CLI → call a plain function.
- Adding Typer next to an argparse or Click CLI → two styles in one tool → extend the existing one.
- Error messages on stdout → break piping → `err=True` (stderr) and a non-zero exit code.

## Sources
- https://typer.tiangolo.com/tutorial/ (fetched 2026-10-08)
- https://typer.tiangolo.com/tutorial/options/ (fetched 2026-10-08)
- https://typer.tiangolo.com/tutorial/subcommands/add-typer/ (fetched 2026-10-08)
- https://typer.tiangolo.com/tutorial/terminating/ (fetched 2026-10-08)
- https://typer.tiangolo.com/tutorial/package/ (fetched 2026-10-08)
- https://docs.python.org/3/library/argparse.html (fetched 2026-10-08)
- https://click.palletsprojects.com/ (fetched 2026-10-08)
