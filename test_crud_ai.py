# test_crud_ai.py

import os
import tempfile
import pytest

import crud_ai


@pytest.fixture
def temp_db():
    """Create a temporary database for each test."""
    fd, path = tempfile.mkstemp()

    original_db = crud_ai.DB_NAME
    crud_ai.DB_NAME = path

    crud_ai.create_table()

    yield path

    crud_ai.DB_NAME = original_db
    os.close(fd)
    os.remove(path)


def test_create_user(temp_db):
    """Test creating a user."""
    crud_ai.create_user("Alice", "alice@example.com", 25)

    users = crud_ai.get_all_users()

    assert len(users) == 1
    assert users[0][1] == "Alice"
    assert users[0][2] == "alice@example.com"
    assert users[0][3] == 25


def test_get_all_users(temp_db):
    """Test retrieving all users."""
    crud_ai.create_user("Alice", "alice@example.com", 25)
    crud_ai.create_user("Bob", "bob@example.com", 30)

    users = crud_ai.get_all_users()

    assert len(users) == 2


def test_get_users_by_name_exact_match(temp_db):
    """Test searching for a specific user."""
    crud_ai.create_user("Alice", "alice@example.com", 25)
    crud_ai.create_user("Bob", "bob@example.com", 30)

    results = crud_ai.get_users_by_name("Alice")

    assert len(results) == 1
    assert results[0][1] == "Alice"


def test_get_users_by_name_partial_match(temp_db):
    """Test partial name search."""
    crud_ai.create_user("Alice Smith", "alice@example.com", 25)
    crud_ai.create_user("Alice Johnson", "alicej@example.com", 30)

    results = crud_ai.get_users_by_name("Alice")

    assert len(results) == 2


def test_update_user_name(temp_db):
    """Test updating a user's name."""
    crud_ai.create_user("Alice", "alice@example.com", 25)

    user_id = crud_ai.get_all_users()[0][0]

    crud_ai.update_user(user_id, name="Alicia")

    updated_user = crud_ai.get_all_users()[0]

    assert updated_user[1] == "Alicia"


def test_update_user_email(temp_db):
    """Test updating a user's email."""
    crud_ai.create_user("Alice", "alice@example.com", 25)

    user_id = crud_ai.get_all_users()[0][0]

    crud_ai.update_user(user_id, email="newalice@example.com")

    updated_user = crud_ai.get_all_users()[0]

    assert updated_user[2] == "newalice@example.com"


def test_update_user_age(temp_db):
    """Test updating a user's age."""
    crud_ai.create_user("Alice", "alice@example.com", 25)

    user_id = crud_ai.get_all_users()[0][0]

    crud_ai.update_user(user_id, age=26)

    updated_user = crud_ai.get_all_users()[0]

    assert updated_user[3] == 26


def test_update_multiple_fields(temp_db):
    """Test updating multiple fields at once."""
    crud_ai.create_user("Alice", "alice@example.com", 25)

    user_id = crud_ai.get_all_users()[0][0]

    crud_ai.update_user(
        user_id,
        name="Alicia",
        email="alicia@example.com",
        age=27
    )

    updated_user = crud_ai.get_all_users()[0]

    assert updated_user[1] == "Alicia"
    assert updated_user[2] == "alicia@example.com"
    assert updated_user[3] == 27


def test_delete_user(temp_db):
    """Test deleting a user."""
    crud_ai.create_user("Alice", "alice@example.com", 25)

    user_id = crud_ai.get_all_users()[0][0]

    crud_ai.delete_user(user_id)

    users = crud_ai.get_all_users()

    assert len(users) == 0


def test_delete_nonexistent_user(temp_db):
    """Deleting a nonexistent user should not raise an error."""
    crud_ai.delete_user(999)

    users = crud_ai.get_all_users()

    assert users == []


def test_duplicate_email_not_inserted(temp_db):
    """Test UNIQUE email constraint."""
    crud_ai.create_user("Alice", "alice@example.com", 25)
    crud_ai.create_user("Bob", "alice@example.com", 30)

    users = crud_ai.get_all_users()

    assert len(users) == 1
    assert users[0][1] == "Alice"


def test_search_no_results(temp_db):
    """Test searching for a non-existent user."""
    crud_ai.create_user("Alice", "alice@example.com", 25)

    results = crud_ai.get_users_by_name("Charlie")

    assert results == []