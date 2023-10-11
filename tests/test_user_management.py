# tests/test_user_management.py

import pytest
import psycopg2
from unittest.mock import MagicMock, patch

from app.modules.user_management import create_user, get_user
from app.db_manager import connect_to_db

# @pytest.mark.parametrize(
#     "user_id, first_name, last_name, username, expected_success, expected_message",
#     [
#         (21, None, "Doe", "doe7", False, "Invalid input: first_name is required and must be a non-empty string."),  # None as first_name
#         (22, "", "Doe", "doe8", False, "Invalid input: first_name is required and must be a non-empty string."),  # Empty string as first_name
#         (23, "محمد", "Doe", "doe9", True, "User created successfully."),  # Persian character as first_name
#         (24, "John", None, "doe10", True, "User created successfully."),  # None as last_name
#         (25, "John", "", "doe11", True, "User created successfully."),  # Empty string as last_name
#         (26, "John", "Doe", None, True, "User created successfully."),  # None as username
#         (27, "John", "Doe", "", True, "User created successfully."),  # Empty string as username
#     ]
# )
# def test_create_user(user_id, first_name, last_name, username, expected_success, expected_message):
#     result = create_user(user_id, first_name, last_name, username)
#     assert result["success"] == expected_success, result["message"]
#     assert result["message"] == expected_message

#     connection = connect_to_db()
#     with connection.cursor() as cursor:
#         cursor.execute("SELECT * FROM lingo_users WHERE user_id = %s;", (user_id,))
#         user = cursor.fetchone()

#     if expected_success:
#         assert user is not None, f"User with user_id {user_id} not found."
#         assert user[1] == first_name, f"Expected first name {first_name}, but got {user[1]}"
#         assert user[2] == last_name, f"Expected last name {last_name}, but got {user[2]}"
#         assert user[3] == username, f"Expected username {username}, but got {user[3]}"
#     else:
#         assert user is None, f"User with user_id {user_id} should not have been created."



# @patch('app.db_manager.connect_to_db') 
# def test_get_user(mock_connect):
#     # Test case 1: User not found
#     mock_connect.return_value = MagicMock()
#     mock_connect.return_value.cursor.return_value.__enter__.return_value.fetchone.return_value = None
#     result = get_user(123)
#     assert result == {"success": False, "message": "User not found."}

#     # # Test case 2: Database connection failed
#     # mock_connect.return_value = None
#     # result = get_user(123)
#     # assert result == {"success": False, "message": "Database connection failed."}


#     # Test case 3: Successful user retrieval
#     mock_connect.return_value = MagicMock()
#     mock_connect.return_value.cursor.return_value.__enter__.return_value.fetchone.return_value = ('John', 'active', '5', 'model1')
#     result = get_user(123)
#     assert result == {
#         "success": True, 
#         "message": "User found.", 
#         "first_name": 'John', 
#         "status": 'active', 
#         "level": '5', 
#         "model": 'model1'
#     }

#     # Test case 4: psycopg2 Error
#     mock_connect.return_value = MagicMock()
#     mock_connect.return_value.cursor.side_effect = psycopg2.Error("Database error")
#     result = get_user('123')
#     assert result["success"] == False
#     assert "An error occurred" in result["message"]


def test_get_user():
    # Test case 1: Invalid user_id
    result = get_user(None)
    assert result == {"success": False, "message": "Invalid input: user_id is required."}

    # Test case 2: User not found
    result = get_user(123)
    assert result == {"success": False, "message": "User not found."}

    # Test case 3: Successful user retrieval
    # You need to ensure that this user_id exists in your test database
    result = get_user(2)  
    assert result["success"] == True
    assert "User found." in result["message"]

    # Test case 4: psycopg2 Error
    # This can be tricky to test because it requires an error to occur in the psycopg2 library.
    # One way to simulate this could be to temporarily modify your get_user function to raise an error when a specific user_id is used.
    result = get_user('error_user_id')
    assert result["success"] == False
    assert "An error occurred" in result["message"]