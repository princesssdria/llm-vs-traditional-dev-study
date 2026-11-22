import sqlite3
import pytest

@pytest.fixture
def db_connection():
    connection = sqlite3.connect(':memory:')
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT, price REAL)''')
    yield cursor
    connection.close()

def test_create_item(db_connection):
    db_connection.execute("INSERT INTO items (name, price) VALUES (?, ?)", ("Test Item", 19.99))
    db_connection.connection.commit()
    db_connection.execute("SELECT * FROM items WHERE name = ?", ("Test Item",))
    assert db_connection.fetchall() == [(1, "Test Item", 19.99)]

def test_read_item(db_connection):
    db_connection.execute("INSERT INTO items (name, price) VALUES (?, ?)", ("Test Item", 19.99))
    db_connection.connection.commit()
    db_connection.execute("SELECT * FROM items WHERE name = ?", ("Test Item",))
    assert db_connection.fetchall() == [(1, "Test Item", 19.99)]

def test_update_item(db_connection):
    db_connection.execute("INSERT INTO items (name, price) VALUES (?, ?)", ("Test Item", 19.99))
    db_connection.connection.commit()
    db_connection.execute("UPDATE items SET price = ? WHERE name = ?", (29.99, "Test Item"))
    db_connection.connection.commit()
    db_connection.execute("SELECT * FROM items WHERE name = ?", ("Test Item",))
    assert db_connection.fetchall() == [(1, "Test Item", 29.99)]

def test_delete_item(db_connection):
    db_connection.execute("INSERT INTO items (name, price) VALUES (?, ?)", ("Test Item", 19.99))
    db_connection.connection.commit()
    db_connection.execute("DELETE FROM items WHERE name = ?", ("Test Item",))
    db_connection.connection.commit()
    db_connection.execute("SELECT * FROM items WHERE name = ?", ("Test Item",))
    assert db_connection.fetchall() == []