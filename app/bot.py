# app/bot.py

### General import

import os
from dotenv import load_dotenv
import traceback
import html
import json
import openai

### Telegram import
import telegram
from telegram import (
    Update,
    BotCommand,
    InputMediaPhoto,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
    CommandHandler,
    CallbackQueryHandler
)
from telegram.constants import ParseMode

### app imports
from app.modules.command_handling import start, send_typing_action


### logging settings
import logging
from app.log_config import configure_logging

my_logger = configure_logging(__name__)
logger_telegram = configure_logging('telegram', False, level=logging.INFO)

### load local envs
load_dotenv()

# openai.api_key = os.environ['OPENAI_API_KEY']
TG_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
ADMIN_TG_USER_ID = os.environ['ADMIN_TG_USER_ID']

@send_typing_action    
async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Handle incoming text messages
    pass  # Implement your code

async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Handle incoming voice messages
    pass  # Implement your code

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:

    my_logger.error("Telegram BOT Exception while handling an update:", exc_info=context.error)

    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )
    limit = 4096
    chunks = [message[i:i + limit] for i in range(0, len(message), limit)]

    for chunk in chunks:
        await context.bot.send_message(
            chat_id=ADMIN_TG_USER_ID, text=chunk, parse_mode=ParseMode.HTML
        )

# FIXME commands should be modified accordingly
# async def post_init(application: Application):
#     await application.bot.set_my_commands([
#         BotCommand("/help", "Help"),
#         BotCommand("/new", "New Conversation"),
#         BotCommand("/balance", "Available credit"),
#         BotCommand("/settings", "Settings"),
#     ]) 


def main():
    application = (
        ApplicationBuilder()
        .token(os.environ['TELEGRAM_BOT_TOKEN'])
        .concurrent_updates(True)
        # .post_init(post_init) #TODO add after post_init function defined
        .build()
    )

    start_handler = CommandHandler('start', start)
    # help_handler = CommandHandler('help', get_help) # TODO add help
    # reset_handler = CommandHandler('reset', get_reset_hist) # TODO
    # balance_handler = CommandHandler('balance', get_balance) # TODO
    # settings_handler = CommandHandler('settings', settings_callback)

    text_message_handler = MessageHandler(
        filters.TEXT & (~filters.COMMAND), handle_text_message
    )

    voice_handler = MessageHandler(filters.VOICE | filters.AUDIO , handle_voice_message)

    application.add_handler(start_handler)
    # application.add_handler(settings_handler)

    application.add_handler(text_message_handler)
    application.add_handler(voice_handler)

    application.add_error_handler(error_handler)

    my_logger.info("Running Lingobot Telegram BOT")
    application.run_polling()

if __name__ == '__main__':
    main()