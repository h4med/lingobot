# tests/test_user_management.py

import pytest
from app.modules import user_management
from app.db_manager import connect_to_db

@pytest.mark.parametrize(
    "user_id, first_name, last_name, username, expected_success, expected_message",
    [
        (21, None, "Doe", "doe7", False, "Invalid input: first_name is required and must be a non-empty string."),  # None as first_name
        (22, "", "Doe", "doe8", False, "Invalid input: first_name is required and must be a non-empty string."),  # Empty string as first_name
        (23, "محمد", "Doe", "doe9", True, "User created successfully."),  # Persian character as first_name
        (24, "John", None, "doe10", True, "User created successfully."),  # None as last_name
        (25, "John", "", "doe11", True, "User created successfully."),  # Empty string as last_name
        (26, "John", "Doe", None, True, "User created successfully."),  # None as username
        (27, "John", "Doe", "", True, "User created successfully."),  # Empty string as username
    ]
)
def test_create_user(user_id, first_name, last_name, username, expected_success, expected_message):
    result = user_management.create_user(user_id, first_name, last_name, username)
    assert result["success"] == expected_success, result["message"]
    assert result["message"] == expected_message

    connection = connect_to_db()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM lingo_users WHERE user_id = %s;", (user_id,))
        user = cursor.fetchone()

    if expected_success:
        assert user is not None, f"User with user_id {user_id} not found."
        assert user[1] == first_name, f"Expected first name {first_name}, but got {user[1]}"
        assert user[2] == last_name, f"Expected last name {last_name}, but got {user[2]}"
        assert user[3] == username, f"Expected username {username}, but got {user[3]}"
    else:
        assert user is None, f"User with user_id {user_id} should not have been created."
