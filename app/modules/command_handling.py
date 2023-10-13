# app/modules/command_handling.py
from functools import wraps

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram.constants import ChatAction

from app.modules.user_management import create_user

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

def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    response = create_user(user_id)
    update.message.reply_text(response['message'])
    ask_for_settings(update, context)

def ask_for_settings(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Set Level", callback_data='set_level'),
         InlineKeyboardButton("Set Model", callback_data='set_model')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please set your preferences:', reply_markup=reply_markup)

def settings_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    if query.data == 'set_level':
        # Handle level setting
        pass  # Implement your code
    elif query.data == 'set_model':
        # Handle model setting
        pass  # Implement your code