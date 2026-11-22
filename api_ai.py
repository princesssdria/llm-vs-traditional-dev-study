"""
Secure API endpoint example: bearer-token auth + strict input validation.

Setup:
    pip install fastapi uvicorn

Generate a token and run:
    export API_TOKENS="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
    echo $API_TOKENS
    uvicorn app:app --reload

Try it:
    curl -X POST http://127.0.0.1:8000/items \
      -H "Authorization: Bearer $API_TOKENS" \
      -H "Content-Type: application/json" \
      -d '{"name": "Widget", "quantity": 3, "tags": ["tools", "small"]}'
"""

import hashlib
import hmac
import os
import re
from itertools import count
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Path, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field, field_validator

# --------------------------------------------------------------------------
# Authentication
# --------------------------------------------------------------------------
# Tokens come from the environment (comma-separated), never from source code.
# They are hashed at startup so plaintext tokens aren't kept in memory longer
# than necessary, and compared in constant time to avoid timing attacks.


def _hash(token: str) -> bytes:
    return hashlib.sha256(token.encode("utf-8")).digest()


VALID_TOKEN_HASHES = [
    _hash(t.strip()) for t in os.environ.get("API_TOKENS", "").split(",") if t.strip()
]

bearer_scheme = HTTPBearer(auto_error=False)


def require_token(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> None:
    # Fail closed: if no tokens are configured, nobody gets in.
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing credentials",  # same message for all failures
        headers={"WWW-Authenticate": "Bearer"},
    )
    if creds is None or not VALID_TOKEN_HASHES:
        raise unauthorized

    presented = _hash(creds.credentials)
    # Check every token (no early exit) so timing doesn't reveal which matched.
    matches = [hmac.compare_digest(presented, valid) for valid in VALID_TOKEN_HASHES]
    if not any(matches):
        raise unauthorized


# --------------------------------------------------------------------------
# Input validation
# --------------------------------------------------------------------------
NAME_PATTERN = re.compile(r"^[\w .,'-]+$", re.UNICODE)
TAG_PATTERN = re.compile(r"^[a-z0-9_-]{1,32}$")


class ItemCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)  # reject unknown fields

    name: str = Field(min_length=1, max_length=100)
    quantity: int = Field(ge=1, le=1000)
    tags: list[str] = Field(default_factory=list, max_length=10)

    @field_validator("name")
    @classmethod
    def name_has_safe_chars(cls, v: str) -> str:
        if not NAME_PATTERN.match(v):
            raise ValueError("name contains invalid characters")
        return v

    @field_validator("tags")
    @classmethod
    def tags_are_valid(cls, v: list[str]) -> list[str]:
        for tag in v:
            if not TAG_PATTERN.match(tag):
                raise ValueError(f"invalid tag: {tag!r} (use a-z, 0-9, _ or -; max 32 chars)")
        return v


class ItemOut(ItemCreate):
    id: int


# --------------------------------------------------------------------------
# App
# --------------------------------------------------------------------------
# Hide interactive docs in production if you don't want them exposed.
app = FastAPI(title="Secure Items API")

_db: dict[int, ItemOut] = {}  # stand-in for a real database
_ids = count(1)


@app.post(
    "/items",
    response_model=ItemOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_token)],
)
def create_item(item: ItemCreate) -> ItemOut:
    new = ItemOut(id=next(_ids), **item.model_dump())
    _db[new.id] = new
    return new


@app.get(
    "/items/{item_id}",
    response_model=ItemOut,
    dependencies=[Depends(require_token)],
)
def get_item(item_id: Annotated[int, Path(ge=1, le=2**31 - 1)]) -> ItemOut:
    item = _db.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.get("/health")
def health() -> dict[str, str]:
    """Unauthenticated liveness check; exposes nothing sensitive."""
    return {"status": "ok"}