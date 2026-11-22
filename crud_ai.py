# crud_ai.py

import sqlite3


DB_NAME = "users.db"


def get_connection():
    """Create and return a database connection."""
    return sqlite3.connect(DB_NAME)


def create_table():
    """Create the users table if it doesn't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            age INTEGER
        )
    """)

    conn.commit()
    conn.close()


def create_user(name, email, age):
    """Insert a new user into the database."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
            (name, email, age)
        )
        conn.commit()
        print(f"User '{name}' created successfully.")
    except sqlite3.IntegrityError as e:
        print(f"Error: {e}")
    finally:
        conn.close()


def get_all_users():
    """Retrieve all users."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    conn.close()
    return users


def get_users_by_name(name):
    """Retrieve users matching a name."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE name LIKE ?",
        (f"%{name}%",)
    )
    users = cursor.fetchall()

    conn.close()
    return users


def update_user(user_id, name=None, email=None, age=None):
    """Update user information."""
    conn = get_connection()
    cursor = conn.cursor()

    updates = []
    values = []

    if name:
        updates.append("name = ?")
        values.append(name)

    if email:
        updates.append("email = ?")
        values.append(email)

    if age is not None:
        updates.append("age = ?")
        values.append(age)

    if not updates:
        print("No fields provided for update.")
        conn.close()
        return

    values.append(user_id)

    query = f"""
        UPDATE users
        SET {', '.join(updates)}
        WHERE id = ?
    """

    cursor.execute(query, values)
    conn.commit()

    if cursor.rowcount:
        print(f"User ID {user_id} updated successfully.")
    else:
        print(f"No user found with ID {user_id}.")

    conn.close()


def delete_user(user_id):
    """Delete a user by ID."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM users WHERE id = ?",
        (user_id,)
    )

    conn.commit()

    if cursor.rowcount:
        print(f"User ID {user_id} deleted successfully.")
    else:
        print(f"No user found with ID {user_id}.")

    conn.close()


def display_users(users):
    """Display users in a readable format."""
    if not users:
        print("No users found.")
        return

    print("\nUsers:")
    print("-" * 50)

    for user in users:
        print(
            f"ID: {user[0]}, "
            f"Name: {user[1]}, "
            f"Email: {user[2]}, "
            f"Age: {user[3]}"
        )
    print("-" * 50)


if __name__ == "__main__":
    create_table()

    # CREATE
    create_user("Alice", "alice@example.com", 25)
    create_user("Bob", "bob@example.com", 30)

    # READ ALL
    print("\nAll Users:")
    display_users(get_all_users())

    # READ/FILTER
    print("\nSearch by name 'Alice':")
    display_users(get_users_by_name("Alice"))

    # UPDATE
    update_user(1, age=26)

    # VERIFY UPDATE
    print("\nAfter update:")
    display_users(get_all_users())

    # DELETE
    delete_user(2)

    # VERIFY DELETE
    print("\nAfter deletion:")
    display_users(get_all_users())