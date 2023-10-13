# app/bot.py

### General import
import logging
import os
from dotenv import load_dotenv
import traceback
import html
import json
import openai

### Telegram import
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
from app.modules.command_handling import start, settings_callback, send_typing_action


### logging settings
logger_telegram = logging.getLogger('telegram')
logger_openai = logging.getLogger('openai')
logger = logging.getLogger(__name__)
logger.propagate = False
logger_telegram.propagate = False
logger_openai.propagate = False

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch_etc = logging.StreamHandler()
ch_etc.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s')
formatter_etc = logging.Formatter('%(asctime)s [%(name)s] - %(levelname)s - %(message)s')

ch.setFormatter(formatter)
ch_etc.setFormatter(formatter_etc)

logger.addHandler(ch)
logger_telegram.addHandler(ch_etc)
logger_openai.addHandler(ch_etc)

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

    logger.error("Telegram BOT Exception while handling an update:", exc_info=context.error)

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

async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("/help", "Help"),
        BotCommand("/image", "Image creation"),
        BotCommand("/reset", "Clear history"),
        BotCommand("/balance", "Available credit"),
        BotCommand("/settings", "Settings"),
    ]) 


def main():
    application = (
        ApplicationBuilder()
        .token(os.environ['TELEGRAM_BOT_TOKEN'])
        .concurrent_updates(True)
        .post_init(post_init)
        .build()
    )
    
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Register command handlers
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(settings_callback))

    # Register message handlers
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text_message))
    dp.add_handler(MessageHandler(Filters.voice, handle_voice_message))

    # Start the bot
    updater.start_polling()

    # Run the bot until the user sends a signal to stop
    updater.idle()

if __name__ == '__main__':
    main()