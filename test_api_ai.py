"""
Tests for api_ai.py

Setup:
    pip install pytest httpx

Run (from the same folder as api_ai.py):
    pytest -v

These tests use their own fake tokens, so you don't need to set
API_TOKENS yourself and your real token is never used.
"""

import os

# The app reads API_TOKENS when it is imported, so set it BEFORE the import.
TOKEN = "test-token-one"
TOKEN_2 = "test-token-two"
os.environ["API_TOKENS"] = f"{TOKEN},{TOKEN_2}"

import pytest
from fastapi.testclient import TestClient

import api_ai

client = TestClient(api_ai.app)

AUTH = {"Authorization": f"Bearer {TOKEN}"}
VALID_ITEM = {"name": "Widget", "quantity": 3, "tags": ["tools", "small"]}


# --------------------------------------------------------------------------
# Health
# --------------------------------------------------------------------------
def test_health_needs_no_token():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


# --------------------------------------------------------------------------
# Authentication
# --------------------------------------------------------------------------
def test_missing_token_is_rejected():
    r = client.post("/items", json=VALID_ITEM)
    assert r.status_code == 401
    assert r.headers["www-authenticate"] == "Bearer"


def test_wrong_token_is_rejected():
    r = client.post("/items", json=VALID_ITEM, headers={"Authorization": "Bearer nope"})
    assert r.status_code == 401


def test_wrong_auth_scheme_is_rejected():
    r = client.post("/items", json=VALID_ITEM, headers={"Authorization": f"Basic {TOKEN}"})
    assert r.status_code == 401


def test_empty_bearer_token_is_rejected():
    r = client.post("/items", json=VALID_ITEM, headers={"Authorization": "Bearer "})
    assert r.status_code == 401


def test_error_message_is_identical_for_missing_and_wrong_token():
    missing = client.post("/items", json=VALID_ITEM)
    wrong = client.post("/items", json=VALID_ITEM, headers={"Authorization": "Bearer nope"})
    assert missing.json() == wrong.json()


def test_get_also_requires_token():
    r = client.get("/items/1")
    assert r.status_code == 401


def test_both_configured_tokens_work():
    for token in (TOKEN, TOKEN_2):
        r = client.post("/items", json=VALID_ITEM, headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 201


def test_fails_closed_when_no_tokens_configured(monkeypatch):
    monkeypatch.setattr(api_ai, "VALID_TOKEN_HASHES", [])
    r = client.post("/items", json=VALID_ITEM, headers=AUTH)
    assert r.status_code == 401


# --------------------------------------------------------------------------
# Creating and fetching items
# --------------------------------------------------------------------------
def test_create_item_success():
    r = client.post("/items", json=VALID_ITEM, headers=AUTH)
    assert r.status_code == 201
    body = r.json()
    assert body["name"] == "Widget"
    assert body["quantity"] == 3
    assert body["tags"] == ["tools", "small"]
    assert isinstance(body["id"], int)


def test_create_then_fetch_item():
    created = client.post("/items", json=VALID_ITEM, headers=AUTH).json()
    r = client.get(f"/items/{created['id']}", headers=AUTH)
    assert r.status_code == 200
    assert r.json() == created


def test_tags_are_optional():
    r = client.post("/items", json={"name": "Widget", "quantity": 1}, headers=AUTH)
    assert r.status_code == 201
    assert r.json()["tags"] == []


def test_name_whitespace_is_trimmed():
    r = client.post("/items", json={"name": "  Widget  ", "quantity": 1}, headers=AUTH)
    assert r.status_code == 201
    assert r.json()["name"] == "Widget"


def test_missing_item_returns_404():
    r = client.get("/items/999999", headers=AUTH)
    assert r.status_code == 404


# --------------------------------------------------------------------------
# Input validation
# --------------------------------------------------------------------------
@pytest.mark.parametrize(
    "payload",
    [
        pytest.param({"quantity": 3}, id="missing-name"),
        pytest.param({"name": "Widget"}, id="missing-quantity"),
        pytest.param({"name": "", "quantity": 3}, id="empty-name"),
        pytest.param({"name": "   ", "quantity": 3}, id="blank-name"),
        pytest.param({"name": "x" * 101, "quantity": 3}, id="name-too-long"),
        pytest.param({"name": "<script>", "quantity": 3}, id="name-html-chars"),
        pytest.param({"name": "a; DROP TABLE items;--", "quantity": 3}, id="name-sql-chars"),
        pytest.param({"name": "Widget", "quantity": 0}, id="quantity-too-low"),
        pytest.param({"name": "Widget", "quantity": -5}, id="quantity-negative"),
        pytest.param({"name": "Widget", "quantity": 1001}, id="quantity-too-high"),
        pytest.param({"name": "Widget", "quantity": "lots"}, id="quantity-not-a-number"),
        pytest.param({"name": "Widget", "quantity": 1.5}, id="quantity-float"),
        pytest.param({"name": "Widget", "quantity": 3, "hacker": True}, id="extra-field"),
        pytest.param({"name": "Widget", "quantity": 3, "tags": ["t"] * 11}, id="too-many-tags"),
        pytest.param({"name": "Widget", "quantity": 3, "tags": ["UPPER"]}, id="tag-uppercase"),
        pytest.param({"name": "Widget", "quantity": 3, "tags": ["has space"]}, id="tag-space"),
        pytest.param({"name": "Widget", "quantity": 3, "tags": ["a" * 33]}, id="tag-too-long"),
        pytest.param({"name": "Widget", "quantity": 3, "tags": "tools"}, id="tags-not-a-list"),
    ],
)
def test_invalid_input_is_rejected(payload):
    r = client.post("/items", json=payload, headers=AUTH)
    assert r.status_code == 422


def test_non_json_body_is_rejected():
    r = client.post(
        "/items",
        content="this is not json",
        headers={**AUTH, "Content-Type": "application/json"},
    )
    assert r.status_code == 422


def test_boundary_values_are_accepted():
    for quantity in (1, 1000):
        r = client.post("/items", json={"name": "Widget", "quantity": quantity}, headers=AUTH)
        assert r.status_code == 201
    r = client.post("/items", json={"name": "x" * 100, "quantity": 1}, headers=AUTH)
    assert r.status_code == 201


@pytest.mark.parametrize("bad_id", ["0", "-1", "abc", "1.5", "99999999999"])
def test_invalid_item_id_is_rejected(bad_id):
    r = client.get(f"/items/{bad_id}", headers=AUTH)
    assert r.status_code == 422


def test_validation_runs_after_auth():
    """Unauthenticated callers should get 401, not a hint about the schema."""
    r = client.post("/items", json={"name": "<script>", "quantity": -1})
    assert r.status_code == 401