# tests/test_command_handling.py

import pytest
from unittest import mock
from telegram import Update, User
from telegram.ext import ContextTypes

from app.modules.command_handling import start
from app.modules.user_management import create_user

@pytest.mark.asyncio
async def test_start():
    # Mocking the Update object from telegram
    update = mock.Mock(spec=Update)
    update.effective_user = User(
        id=12345, 
        first_name="John", 
        last_name="Doe", 
        username="johndoe"
    )

    # Mocking the ContextTypes.DEFAULT_TYPE object
    context = mock.Mock(spec=ContextTypes.DEFAULT_TYPE)

    # Mocking the create_user function to return a successful response
    with mock.patch.object(create_user, 'return_value', {"success": True, "message": "User created successfully."}):
        # Call the start handler
        await start(update, context)

        # Check if send_message was called with the expected arguments
        context.bot.send_message.assert_called_once_with(
            chat_id=12345,
            text="Welcome John!...",  # assuming start_message = "Welcome {name}!..."
            parse_mode="HTML"
        )
