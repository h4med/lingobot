# tests/test_db_manager.py

import pytest
from app import db_manager

def test_connect_to_db():
    connection = db_manager.connect_to_db()
    assert connection is not None, "Database connection failed."
    assert connection.closed == 0, "Connection is not open."
    connection.close()  # Don't forget to close the connection after the test.
