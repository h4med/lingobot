# tests/test_user_management.py

import pytest
from app.modules import user_management
from app.db_manager import connect_to_db

def test_create_user():
    user_id = 1
    first_name = "John"
    last_name = "Doe"
    username = "johndoe"

    result = user_management.create_user(user_id, first_name, last_name, username)
    assert result["success"] is True, result["message"]

    connection = connect_to_db()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM lingo_users WHERE user_id = %s;", (user_id,))
        user = cursor.fetchone()
    assert user is not None, f"User with user_id {user_id} not found."
    assert user[1] == first_name, f"Expected first name {first_name}, but got {user[1]}"
    assert user[2] == last_name, f"Expected last name {last_name}, but got {user[2]}"
    assert user[3] == username, f"Expected username {username}, but got {user[3]}"
