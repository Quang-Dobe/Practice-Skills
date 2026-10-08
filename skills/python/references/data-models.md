# Data Models

> Load when: data classes, pydantic models, validating input data, settings, environment variables, `.env` config. Pinned: Python 3.14, uv 0.12, ruff 0.16, mypy 2.4, pytest 9, pydantic 2.13, FastAPI 0.142, SQLAlchemy 2.1.

## Existing repo
- How to recognise it: `@dataclass` imports, `pydantic` in `pyproject.toml` (check `BaseModel`, `model_validate` vs `parse_obj` to tell v2 from v1), `attrs` / `attr.s` classes, `BaseSettings` imports, `.env.example`.
- Rule: follow what is there. Keep attrs where it is used; keep pydantic v1 style in a v1 codebase and do not upgrade it unasked.
- Match the repo's model for settings (pydantic-settings, dynaconf, plain `os.environ`).

## New repo default
- Pydantic v2 `BaseModel` at boundaries: request bodies, config files, external API payloads, anything untrusted. Plain `dataclass` for internal data that is already validated.
- Validate with `Model.model_validate(data)` (dict) or `Model.model_validate_json(text)`; serialize with `model_dump()` / `model_dump_json()`.
- Constraints with `Field(...)`; custom checks with `@field_validator("name")` stacked on `@classmethod`; model options with `model_config = ConfigDict(...)` (e.g. `extra="forbid"`, `frozen=True`, `from_attributes=True`).
- Dataclasses: `frozen=True` for value objects, `slots=True` for many small instances, `kw_only=True` for wide constructors, `field(default_factory=list)` for mutable defaults.
- Settings: `pydantic_settings.BaseSettings` with `SettingsConfigDict(env_file=".env", env_prefix="APP_", extra="ignore")`. A field without a default is required; a missing one raises `ValidationError` when `Settings()` is built, so construct it once at startup and fail fast. Set `extra="ignore"`: the default `forbid` rejects unrelated keys in a shared `.env`.
- Never open the real `.env`; document keys in `.env.example`.

```python
from dataclasses import dataclass, field

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class UserIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=50)
    email: str

    @field_validator("email")
    @classmethod
    def email_has_at(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("must contain @")
        return v.lower()


@dataclass(frozen=True, slots=True)
class User:
    name: str
    email: str
    tags: tuple[str, ...] = field(default_factory=tuple)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_", extra="ignore")

    database_url: str  # required: missing -> ValidationError at startup
    debug: bool = False


payload = UserIn.model_validate({"name": "Ada", "email": "ADA@example.com"})
user = User(**payload.model_dump())
```

## Avoid
- v1 names `parse_obj`, `.dict()`, `.json()`, `@validator`, `@root_validator`, inner `class Config` → removed or deprecated in v2 → `model_validate`, `model_dump`, `model_dump_json`, `@field_validator`, `@model_validator`, `model_config`.
- `BaseSettings` imported from `pydantic` → it lives in the separate `pydantic_settings` package in v2 → `from pydantic_settings import BaseSettings`.
- Mutable default `tags: list = []` in a dataclass → shared between instances (dataclasses reject it) → `field(default_factory=list)`.
- Pydantic models for every internal struct → validation cost and coupling for no gain → plain dataclass once data is validated.
- Reading `os.environ` all over the code → config errors surface late → one `Settings` object built at startup.

## Sources
- https://docs.python.org/3/library/dataclasses.html (fetched 2026-10-08)
- https://pydantic.dev/docs/validation/latest/concepts/models/ (fetched 2026-10-08; the brief's docs.pydantic.dev URL redirects here)
- https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings/ (fetched 2026-10-08; redirect target of docs.pydantic.dev/latest/concepts/pydantic_settings/)
- https://pydantic.dev/docs/validation/latest/get-started/migration/ (fetched 2026-10-08; redirect target of the migration page)
- https://www.attrs.org/ and https://www.attrs.org/en/stable/overview.html (fetched 2026-10-08; names `attrs.define`, `attrs.field`)
