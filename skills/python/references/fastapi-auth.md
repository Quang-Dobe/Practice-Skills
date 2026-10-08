# FastAPI Auth

> Load when: FastAPI auth, OAuth2, JWT, security dependencies, roles, protected endpoints. Pinned: Python 3.14, uv 0.12, ruff 0.16, mypy 2.4, pytest 9, pydantic 2.13, FastAPI 0.142, SQLAlchemy 2.1.

## Existing repo
- How to recognise it: `OAuth2PasswordBearer`, `HTTPBearer`, `Security(`; imports of `jwt`, `jose`, `passlib`, `pwdlib`, `authlib`; a `get_current_user` dependency; IdP settings (issuer, JWKS URL).
- Rule: follow what is there. Keep its token library, hashing scheme and claim names; never swap them unasked.

## New repo default
- The sample's `User`, `SettingsDep` (settings with `secret_key`, `algorithm`, `token_minutes`) and `load_user` are app code.
- Flow: `OAuth2PasswordBearer(tokenUrl="token")`; `POST /token` takes `OAuth2PasswordRequestForm` and returns `{"access_token": ..., "token_type": "bearer"}`.
- Libraries the FastAPI security tutorial uses today: PyJWT (`uv add pyjwt`, `import jwt`) and pwdlib with Argon2 (`uv add "pwdlib[argon2]"`, `PasswordHash.recommended()`).
- Token creation: `jwt.encode({"sub": username, "exp": datetime.now(UTC) + timedelta(minutes=settings.token_minutes)}, settings.secret_key, algorithm=settings.algorithm)`; the `/token` endpoint returns it. Decode (below) always passes an explicit `algorithms=[...]` list and `options={"require": ["exp", "sub"]}` (PyJWT docs), so tokens without an expiry are refused; an expired `exp` is rejected by `decode`.
- `get_current_user` is a dependency that returns the user or raises 401 with `WWW-Authenticate: Bearer` (also when the token's `sub` no longer maps to a user). Alias it once: `CurrentUser = Annotated[User, Depends(get_current_user)]`.
- Unknown username: still verify the password against a dummy hash, and raise the same 401 as for a wrong password, so neither timing nor message reveals whether the user exists (the tutorial uses the dummy hash).
- Roles: a dependency factory (`require_role("admin")`) layered on `CurrentUser`. Scopes: `OAuth2PasswordBearer(scopes={...})`, `Security(dep, scopes=["items"])`, and `SecurityScopes` inside the dependency.
- Secret key, algorithm and expiry minutes come from settings, never literals (the tutorial's sample key is a placeholder). Short expiry.
- 401 = missing/invalid/expired credentials (send `WWW-Authenticate`); 403 = authenticated but not allowed. The scopes tutorial raises 401 for missing scopes; use 403 for role denial when your API contract distinguishes them.
- External IdP / OIDC: the service only validates tokens. Fetch the IdP's JWKS (`jwt.PyJWKClient`), check signature, `iss`, `aud`, `exp`; do not issue tokens or store passwords.

```python
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

TokenDep = Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl="token"))]
password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash("dummy")

def unauthorized(detail: str) -> HTTPException:
    return HTTPException(status.HTTP_401_UNAUTHORIZED, detail, {"WWW-Authenticate": "Bearer"})

def authenticate(user: User | None, password: str) -> User:
    hashed = user.hashed_password if user else DUMMY_HASH  # same work if unknown
    if not password_hash.verify(password, hashed) or user is None:
        raise unauthorized("Incorrect username or password")
    return user

async def get_current_user(token: TokenDep, settings: SettingsDep) -> User:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm],
                             options={"require": ["exp", "sub"]})
    except jwt.InvalidTokenError:
        raise unauthorized("Could not validate credentials") from None
    if (user := await load_user(payload["sub"])) is None:
        raise unauthorized("Could not validate credentials")
    return user
```

## Avoid
- Hard-coded or committed secret keys → forgeable tokens → settings/environment.
- `jwt.decode` without `algorithms=` → algorithm confusion → pin the list.
- Plain or fast-hash (MD5/SHA) passwords → trivial cracking → pwdlib Argon2 (or the repo's existing scheme).
- 403 for a bad token, or 401 for a valid user lacking a role → breaks client retry logic → 401 vs 403 as above.
- Issuing your own tokens when an IdP exists → a second identity system → validate the IdP's tokens.

## Sources
- https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/ (fetched 2026-10-08)
- https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/ (fetched 2026-10-08)
- https://pyjwt.readthedocs.io/ (fetched 2026-10-08)
