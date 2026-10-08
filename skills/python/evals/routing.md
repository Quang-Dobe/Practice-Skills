# Python routing evals

Each prompt assumes the `python` skill is loaded. Pass = agent opens every `expect` file, none of the `must-not` files, and shows `behavior` when given. Unless the prompt says otherwise, assume the repo already has .claude/conventions/python.md.

## E01
prompt: Start a new Python command-line tool in this empty folder (no .claude/conventions/python.md).
expect: choose-conventions.md, project-structure.md
must-not: detect-conventions.md

## E02
prompt: Repo has pyproject.toml and uv.lock but no .claude/conventions/python.md. Rename get_user to fetch_user across src/.
expect: detect-conventions.md, python-style.md
must-not: choose-conventions.md

## E03
prompt: Review this function for style issues: `def GetData(x): return [i for i in x if i != None]`
expect: python-style.md
must-not: docker.md, database.md

## E04
prompt: mypy reports 40 "Missing type parameters for generic type" errors in repository.py; fix the annotations.
expect: typing.md
must-not: docker.md

## E05
prompt: Load app settings from environment variables and fail at startup if DATABASE_URL is missing.
expect: data-models.md
must-not: docker.md

## E06
prompt: Run 20 jobs concurrently and cancel all of them if any one takes longer than 5 seconds.
expect: async.md
must-not: database.md

## E07
prompt: Our code raises bare Exception("failed") everywhere; set up a proper exception hierarchy and log failures with context.
expect: errors-and-logging.md
must-not: docker.md

## E08
prompt: Where should a new billing package live, and what belongs in its __init__.py?
expect: project-structure.md
must-not: docker.md

## E09
prompt: Add rich as a dependency and pin the project to Python 3.13.
expect: uv-and-environments.md
must-not: lint-format.md

## E10
prompt: Replace black, isort and flake8 with a single tool and run it before each commit.
expect: lint-format.md
must-not: testing.md

## E11
prompt: Write pytest tests for parse_duration() covering five input cases.
expect: testing.md
must-not: fastapi-testing.md

## E12
prompt: Write a Dockerfile for this project with a small final image.
expect: docker.md
must-not: testing.md

## E13
prompt: Call the payments API with a 10-second timeout and retry three times on 503.
expect: http-clients.md
must-not: database.md

## E14
prompt: Add an orders table and create the migration for it.
expect: database.md
must-not: docker.md

## E15
prompt: Add an export subcommand with a --format option to our command-line tool.
expect: cli.md
must-not: database.md

## E16
prompt: Create a new FastAPI app with users and orders routers and one database session per request.
expect: fastapi-structure.md
must-not: cli.md

## E17
prompt: Add a FastAPI endpoint POST /orders that validates the body and returns 409 if the order already exists.
expect: fastapi-endpoints.md
must-not: cli.md

## E18
prompt: Protect the /admin endpoints of our FastAPI app so only callers with a valid JWT and the admin role get through.
expect: fastapi-auth.md
must-not: cli.md

## E19
prompt: Test the FastAPI endpoint GET /orders/{id}, replacing the real database dependency with a fake.
expect: fastapi-testing.md
must-not: docker.md

## E20
prompt: Repo has pyproject.toml but no .claude/conventions/python.md. Build a LangGraph graph with a checkpointer that remembers the conversation.
expect: none
must-not: detect-conventions.md, choose-conventions.md, python-style.md
behavior: says LangGraph/LangChain work belongs to the ai-workflow skill, not this one

## E21
prompt: Repo has a Django project (manage.py, pyproject.toml) and no .claude/conventions/python.md. Add a Django view and template for the profile page.
expect: none
must-not: detect-conventions.md, choose-conventions.md, fastapi-endpoints.md
behavior: says Django is out of scope for this skill

## E22
prompt: Repo has only package.json and no Python files. Build a React component for the login form.
expect: none
must-not: detect-conventions.md, choose-conventions.md, python-style.md

## E23
prompt: Repo has pyproject.toml but no .claude/conventions/python.md. Load sales.csv with pandas and plot monthly totals in a notebook.
expect: none
must-not: detect-conventions.md, choose-conventions.md, python-style.md
behavior: says the data-science stack is out of scope for this skill

## E24
prompt: .claude/conventions/python.md says "types: mypy", but the package I'm editing has pyrightconfig.json and pyright ignore comments. Add type hints to loader.py.
expect: none
must-not: detect-conventions.md, choose-conventions.md
behavior: flags the mismatch and asks which wins before writing code

## E25
prompt: .claude/conventions/python.md lists "manager: poetry". Add requests as a dependency.
expect: uv-and-environments.md
must-not: detect-conventions.md
behavior: uses poetry; does not propose switching to uv

## E26
prompt: Add a FastAPI endpoint that calls the inventory service with httpx, retrying on timeouts, and returns the combined result.
expect: fastapi-endpoints.md, http-clients.md
must-not: cli.md

## E27
prompt: Repo root has services/api (FastAPI, pyproject.toml) and web/ (React, package.json), no .claude/conventions/python.md. Add a health-check endpoint to services/api.
expect: detect-conventions.md, fastapi-endpoints.md
must-not: choose-conventions.md
behavior: scopes the convention scan to services/api and the repo root, not web/

## E28
prompt: Add a FastAPI endpoint that streams a LangGraph agent's output to the browser over SSE.
expect: fastapi-endpoints.md
must-not: choose-conventions.md
behavior: handles the FastAPI streaming part and says the LangGraph part belongs to the ai-workflow skill
