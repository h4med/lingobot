# tests/test_user_management.py

import pytest
import psycopg2
from unittest.mock import MagicMock, patch, Mock

from app.modules import user_management
from app.db_manager import connect_to_db

def test_create_user(monkeypatch):
    mock_connection = MagicMock()
    monkeypatch.setattr(user_management, 'connect_to_db', lambda: mock_connection)

    mock_cursor = MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

    # TODO: Add more test cases for all wiered possible situations
    test_cases = [
        (1, "John", None, "john_doe", True, "User created successfully."),
        (2, None, "Doe", "null_john", False, "Invalid input: first_name is required and must be a non-empty string."),
        (3, "", "Doe", "empty_john", False, "Invalid input: first_name is required and must be a non-empty string."),
        (4, " محمد علی", "Doe", "persian_john", True, "User created successfully."),
        (5, "حسنـــک #۵", "Doe", None, True, "User created successfully."),
    ]

    for user_id, first_name, last_name, username, expected_success, expected_message in test_cases:
        result = user_management.create_user(user_id, first_name, last_name, username)
        assert result["success"] == expected_success, f"Failed for user_id: {user_id}"
        assert result["message"] == expected_message, f"Failed for user_id: {user_id}"

        mock_cursor.reset_mock()
        mock_connection.reset_mock()

def test_get_user(monkeypatch):
    mock_connection = MagicMock()
    monkeypatch.setattr(user_management, 'connect_to_db', lambda: mock_connection)

    mock_cursor = MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

    # Test cases
    test_cases = [
        (1, True, "User found.", "John", "Doe", "john_doe", "ena", 50000, 2, "GPT-3.5", 0),
        (None, False, "Invalid input: user_id is required.", None, None, None, None, None, None, None, None),
        (2, False, "User not found.", None, None, None, None, None, None, None, None),
        (3, True, "User found.", "Jane", "Smith", "jane_smith", "ena", 48000, 2, "GPT-3.5", 10),
        (4, True, "User found.", "Mike", "Johnson", "mike_j", "dis", 45000, 3, "GPT-3.5", 20),
        (5, True, "User found.", "Emily", "Clark", "emily_c", "zer", 42000, 1, "GPT-3.5", 30),
        (6, True, "User found.", "محمد", "علی", "mohammad_a", "ena", 40000, 4, "GPT-3.5", 40),
        (7, True, "User found.", "Anna", "Lee", "anna_l", "dis", 37000, 2, "GPT-3.5", 50),
        (8, True, "User found.", "Chris", "Williams", "chris_w", "zer", 34000, 3, "GPT-3.5", 60),
        (9, True, "User found.", "Olivia", "Taylor", "olivia_t", "ena", 31000, 1, "GPT-3.5", 70),
        (10, True, "User found.", "Daniel", "Anderson", "daniel_a", "dis", 28000, 4, "GPT-3.5", 80),
        (11, True, "User found.", "Sophia", "Martin", "sophia_m", "zer", 25000, 2, "GPT-3.5", 90),
        (12, True, "User found.", "David", "Lewis", "david_l", "ena", 22000, 3, "GPT-3.5", 100),
        (13, True, "User found.", "Mia", "Walker", "mia_w", "dis", 19000, 1, "GPT-3.5", 110),
        (14, True, "User found.", "Matthew", "Harris", "matthew_h", "zer", 16000, 4, "GPT-3.5", 120),
        (15, True, "User found.", "Abigail", "Robinson", "abigail_r", "ena", 13000, 2, "GPT-3.5", 130),
        (16, True, "User found.", "James", "Young", "james_y", "dis", 10000, 3, "GPT-3.5", 140),
        (17, True, "User found.", "Isabella", "King", "isabella_k", "zer", 7000, 1, "GPT-3.5", 150),
        (18, True, "User found.", "Alex", "Scott", "alex_s", "ena", 4000, 4, "GPT-4.0", 160),
        (19, True, "User found.", "Sarah", "Green", "sarah_g", "dis", 1000, 2, "GPT-3.5", 170),
        (20, False, "User not found.", None, None, None, None, None, None, None, None)
    ]

    for user_id, expected_success, expected_message, first_name, last_name, username, status, credit, level, model, request_count in test_cases:
        mock_cursor.fetchone.return_value = None if expected_success is False else (first_name, last_name, username, status, credit, level, model, request_count)
        result = user_management.get_user(user_id)
        assert result["success"] == expected_success, f"Failed for user_id: {user_id}"
        assert result["message"] == expected_message, f"Failed for user_id: {user_id}"

        if expected_success:
            assert result["first_name"] == first_name
            assert result["last_name"] == last_name
            assert result["username"] == username
            assert result["status"] == status
            assert result["credit"] == credit
            assert result["level"] == level
            assert result["model"] == model
            assert result["request_count"] == request_count

        mock_cursor.reset_mock()
        mock_connection.reset_mock()
