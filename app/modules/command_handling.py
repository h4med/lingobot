# app/modules/command_handling.py

from functools import wraps

import telegram

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update

from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from telegram.constants import ChatAction, ParseMode

from app.modules.user_management import create_user
from app.messages.responses import start_message, start_message_back
from app.log_config import configure_logging

logger = configure_logging(__name__)

def send_action(action):
    def decorator(func):
        @wraps(func)
        async def command_func(update, context, *args, **kwargs):
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id, 
                action=action,
                )
            return await func(update, context,  *args, **kwargs)
        return command_func
    return decorator

send_typing_action = send_action(ChatAction.TYPING)
send_photo_action = send_action(ChatAction.UPLOAD_PHOTO)
send_voice_action = send_action(ChatAction.RECORD_VOICE)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user 
    logger.info(f'Received /start first_name: {user.first_name}, last_name: {user.last_name}, username: {user.username}, ID: {user.id}')

    response = create_user(user.id, user.first_name, user.last_name, user.username)

    if response["success"]:
        message = start_message.format(name=user.first_name)
        logger.info(f'User: {user.first_name} with ID: {user.id} successfully added to users')
    else:
        if response["message"] =="User already exists":
            message = start_message_back.format(name=user.first_name)
            logger.info(f'User: {user.first_name} with ID: {user.id} came back!')
        else:
            message = "Sorry this error occured: " + response["message"]
            logger.error(f'Adding New User: {user.first_name} with ID: {user.id} to users. Error: {response["message"]}')

    await context.bot.send_message(
        chat_id=user.id, 
        text=message,
        parse_mode=ParseMode.HTML
        )
