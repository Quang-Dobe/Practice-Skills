# Docker

> Load when: Dockerfile, container image. Pinned: Python 3.14, uv 0.12, ruff 0.16, mypy 2.4, pytest 9, pydantic 2.13, FastAPI 0.142, SQLAlchemy 2.1.

## Existing repo
- Recognise it: `Dockerfile`, `*.dockerfile`, `.dockerignore`, `compose.yaml` / `docker-compose.yml`, CI build steps.
- Rule: follow what is there (base image, package installer, entrypoint). Do not rewrite a pip or poetry Dockerfile to uv unasked.

## New repo default
- Multi-stage: a `builder` stage installs with uv; the final stage copies only `/app/.venv`, so uv and sources stay out of the image.
- Copy the uv binary from a pinned image: `COPY --from=ghcr.io/astral-sh/uv:<version> /uv /uvx /bin/`.
- Dependency layer first: bind-mount `uv.lock` and `pyproject.toml`, run `uv sync --locked --no-install-project --no-dev`; then copy the project and run `uv sync --locked --no-editable --no-dev` (the `dev` group syncs by default; `--no-dev` keeps ruff, mypy and pytest out of the image).
- Builder stage env (as in the snippet): `UV_LINK_MODE=copy` (needed with cache mounts), `UV_COMPILE_BYTECODE=1`, `UV_PYTHON_DOWNLOADS=0`. Final stage: `PYTHONUNBUFFERED=1` so logs flush immediately (a common container choice, not sourced from the uv page).
- Pin the base image tag (python slim variant), never `latest`. Run as a non-root user (general container practice, not stated on the uv page).
- `.dockerignore` must list `.venv` (also `.git`, `__pycache__`, `.env*`).
- FastAPI: exec-form `CMD ["fastapi", "run", ...]`, so shutdown is graceful and lifespan events run; add `--proxy-headers` behind a TLS proxy. Point it at the app with `--entrypoint pkg.module:app` or `[tool.fastapi] entrypoint` in `pyproject.toml`; the CLI ships with `fastapi[standard]`.

```dockerfile
FROM python:3.14-slim-trixie AS builder
COPY --from=ghcr.io/astral-sh/uv:0.12.23 /uv /uvx /bin/
ENV UV_LINK_MODE=copy UV_COMPILE_BYTECODE=1 UV_PYTHON_DOWNLOADS=0
WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable --no-dev

FROM python:3.14-slim-trixie
RUN useradd --create-home app
COPY --from=builder --chown=app:app /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1
USER app
WORKDIR /home/app
EXPOSE 8000
CMD ["fastapi", "run", "--entrypoint", "my_pkg.main:app", "--port", "8000", "--proxy-headers"]
```

## Avoid
- Shell-form `CMD fastapi run ...` → the app is not PID 1, graceful shutdown and lifespan break → exec (JSON) form.
- `COPY . .` before the dependency layer → every code change reinstalls dependencies → lock files first, sources after.
- Copying the host `.venv` into the image → wrong platform and bloat → `.dockerignore` it.
- The deprecated `tiangolo/uvicorn-gunicorn-fastapi` base image → FastAPI docs say not to use it → official Python image.
- `latest` tags and root user → unreproducible builds, larger blast radius → pinned tags, `USER app`.

## Sources
- https://docs.astral.sh/uv/guides/integration/docker/ (fetched 2026-10-08)
- https://fastapi.tiangolo.com/deployment/docker/ (fetched 2026-10-08)
- https://docs.docker.com/build/building/multi-stage/ (fetched 2026-10-08)
- https://fastapi.tiangolo.com/fastapi-cli/ (fetched 2026-10-08)
