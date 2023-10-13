# tests/test_message_processing.py

import pytest
from unittest.mock import MagicMock, Mock
from app.modules.message_processing import add_conversation, get_conversations, delete_conversations
from app.db_manager import connect_to_db

def test_add_conversation(monkeypatch):
    mock_connection = MagicMock()
    monkeypatch.setattr('app.modules.message_processing.connect_to_db', lambda: mock_connection)

    mock_cursor = MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

    test_cases = [
        (1, "Hello!", "user", True, "Conversation added successfully."),
        (None, "Hello!", "user", False, "Invalid input: user_id is required and must be a positive integer."),
        (1, "", "user", False, "Invalid input: message is required and must be a non-empty string."),
        (1, "Hello!", "alien", False, "Invalid input: sent_by must be either 'user' or 'bot'."),
        (2, "Good morning!", "user", True, "Conversation added successfully."),
        (2, "Good morning!", "bot", True, "Conversation added successfully."),
        (3, None, "user", False, "Invalid input: message is required and must be a non-empty string."),
        (3, "How are you?", None, False, "Invalid input: sent_by must be either 'user' or 'bot'."),
        (-1, "Negative user ID", "user", False, "Invalid input: user_id is required and must be a positive integer."),
        (0, "Zero user ID", "bot", False, "Invalid input: user_id is required and must be a positive integer."),
        (1, "   ", "user", False, "Invalid input: message is required and must be a non-empty string."),
        (1, "\t\n", "user", False, "Invalid input: message is required and must be a non-empty string."),
        (1, "Hello!", "USER", True, "Conversation added successfully."),
        (1, "Hello!", "  user  ", True, "Conversation added successfully."),
        (1, "Hello!", "user  ", True, "Conversation added successfully."),  
        (1, "Hello!", "  user", True, "Conversation added successfully."),  
        (4, "Special characters !@#$%^&*()", "user", True, "Conversation added successfully."),
        (5, "Emoji 😄", "user", True, "Conversation added successfully."),
        (6, "Unicode 你好", "user", True, "Conversation added successfully."),
        (7, " Long message " + "a" * 10000, "user", True, "Conversation added successfully."),         
    ]

    for user_id, message, sent_by, expected_success, expected_message in test_cases:
        result = add_conversation(user_id, message, sent_by)
        print(f'Testing with: {user_id}, {message}, {sent_by}, result: {result}')
        assert result["success"] == expected_success
        assert result["message"] == expected_message

        mock_cursor.reset_mock()
        mock_connection.reset_mock()


test_cases = [
    (1, 20, True, "Success"), 
    (0, 20, False, "Invalid input: user_id is required and must be a positive integer."),  # Invalid user_id
    (1, 0, False, "Invalid input: limit must be a positive integer."),  # Invalid limit
]

def mock_connect_to_db():
    class MockConnection:
        def cursor(self):
            return MockCursor()
        def close(self):
            pass
        def commit(self):
            pass
        def rollback(self):
            pass
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    class MockCursor:
        def execute(self, query, params):
            pass
        def fetchall(self):
            return [
                ("Hello!", "user", "2023-10-06 10:00:00"),
                ("Hi there!", "bot", "2023-10-06 10:01:00"),
                ("user_id is required and must be a positive integer.user_id is required and must be a positive integer.", "user", "2023-10-06 10:01:00"),
                ("user_id is required and must be a positive integer.user_id is required and must be a positive integer.", "user", "2023-10-06 10:01:00"),
                ("user_id is required and must be a positive integer.user_id is required and must be a positive integer.", "bot", "2023-10-06 10:01:00"),
            ]
        def __enter__(self):
            return self  
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass  

    return MockConnection()

def test_get_conversations(monkeypatch):
    monkeypatch.setattr("app.modules.message_processing.connect_to_db", mock_connect_to_db)
    
    for user_id, limit, expected_success, expected_message in test_cases:
        result = get_conversations(user_id, limit)
        assert result["success"] == expected_success
        if expected_success:
            assert "conversations" in result
        else:
            assert result["message"] == expected_message

def test_delete_conversations(monkeypatch):
    monkeypatch.setattr("app.modules.message_processing.connect_to_db", mock_connect_to_db)
    
    test_cases = [
        (1, True, "Conversations deleted successfully."), 
        (0, False, "Invalid input: user_id is required and must be a positive integer."), 

    ]

    for user_id, expected_success, expected_message in test_cases:
        result = delete_conversations(user_id)
        assert result["success"] == expected_success
        assert result["message"] == expected_message