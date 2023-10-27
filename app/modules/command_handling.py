# app/modules/command_handling.py

import os
from dotenv import load_dotenv
from functools import wraps

from telegram import InlineKeyboardMarkup, Update

from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from telegram.constants import ChatAction, ParseMode

from app.modules.user_management import create_user, get_user, update_user_credit_req_count, update_user_settings
from app.modules.message_processing import delete_conversations, add_conversation, get_conversations
from app.modules.openai_api import create_chat_completion, count_tokens
from app.messages.responses import start_message, start_message_back
from app.messages.prompts import system_prompt, user_new_conv_start
from app.messages.menu import settings_main_menu, settings_level_list_menu
from app.log_config import configure_logging
from app.helpers.utils import check_user_status, log_and_return

logger = configure_logging(__name__)

load_dotenv()

# openai.api_key = os.environ['OPENAI_API_KEY']
max_token_chat = int(os.environ['CHATCOMPLETION_MAX_TOKEN'])
max_token_chat_free = int(os.environ['CHATCOMPLETION_MAX_TOKEN_FREE'])

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
    logger.info(f'Received /start first_name: {user.first_name}, last_name: {user.last_name}, username: {user.username}, ID: {user.id}, is_bot: {user.is_bot}')

    response = create_user(user.id, user.first_name, user.is_bot, user.last_name, user.username)

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

@send_typing_action
async def handle_new_conv_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.edited_message or not update.message or update.message.via_bot:
        return

    user = update.effective_user
    logger.info(f"Received New Conversation Command from User: {user.first_name} with ID: {user.id}")

    user_data = get_user(user.id)

    if not user_data["success"]:
        await context.bot.send_message(chat_id=user.id, text=log_and_return("get_user", user, user_data), parse_mode=ParseMode.HTML)
        return

    status_result = check_user_status(
        user_status=user_data["status"],
        is_bot=user_data["is_bot"],
        req_count=user_data["request_count"]
    )
    if not status_result["success"]:
        await context.bot.send_message(chat_id=user.id, text=log_and_return("check_user_status", user, status_result), parse_mode=ParseMode.HTML)
        return

    deletion_result = delete_conversations(user.id)
    if not deletion_result["success"]:
        await context.bot.send_message(chat_id=user.id, text=log_and_return("delete_conversations", user, deletion_result), parse_mode=ParseMode.HTML)
        return

    prompt = system_prompt.format(user_name=user_data["first_name"], user_skill_level=user_data["level"])

    add_result = add_conversation(user.id, prompt, "system")
    if not add_result["success"]:
        await context.bot.send_message(chat_id=user.id, text=log_and_return("add_conversation", user, add_result), parse_mode=ParseMode.HTML)
        return

    max_token = max_token_chat_free if user_data["status"] == 'zer' else max_token_chat

    query = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": user_new_conv_start}
    ]

    chat_result = await create_chat_completion(query, max_token)
    if not chat_result["success"]:
        await context.bot.send_message(chat_id=user.id, text=log_and_return("create_chat_completion", user, chat_result), parse_mode=ParseMode.HTML)
        return

    # logger.info(f'create_chat_completion_result: {user.first_name} with ID: {user.id}. message: {chat_result["content"]}\nToken; {chat_result["total_tokens"]}')

    credit_update_result = update_user_credit_req_count(user.id, user_data["credit"], user_data["request_count"], chat_result["total_tokens"])
    if not credit_update_result["success"]:
        await context.bot.send_message(chat_id=user.id, text=log_and_return("update_user_credit_req_count", user, credit_update_result), parse_mode=ParseMode.HTML)
        return

    await context.bot.send_message(chat_id=user.id, text=chat_result["content"], parse_mode=ParseMode.HTML)
    #TODO: text to speech

async def handle_settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.edited_message or not update.message or update.message.via_bot:
        return

    user = update.effective_user
    logger.info(f"Received New Conversation Command from User: {user.first_name} with ID: {user.id}")

    user_data = get_user(user.id)

    if not user_data["success"]:
        await context.bot.send_message(chat_id=user.id, text=log_and_return("get_user", user, user_data), parse_mode=ParseMode.HTML)
        return
    
    user_level=user_data["level"]
    keyboard = settings_main_menu(user_level)

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Settings", reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.message.chat.id
    user_data = get_user(user_id)

    if not user_data["success"]:
        await context.bot.send_message(chat_id=user_id, text=f'get_user Error: {user_data["message"]}', parse_mode=ParseMode.HTML)
        return
    
    user_level=user_data["level"]

    if query.data == 'level':
        keyboard = settings_level_list_menu()
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Set Your Skill Level", reply_markup=reply_markup)
    
    elif query.data.startswith('level_'):
        level = query.data.split('_')[1]
        update_settings_result = update_user_settings(user_id, int(level))
        logger.info(f"Updating level, ID: {user_id}, to: {level}")
        if not update_settings_result["success"]:
            logger.error(f"Error updating level, ID: {user_id}, Error: {update_settings_result['message']}")
            await query.edit_message_text(text="Error updating level")
            return
        level_map = {
            "1": "Beginner",
            "2": "Elementary",
            "3": "Intermediate",
            "4": "Upper-Intermediate",
            "5": "Advanced",
        }
        user_skill_level=level_map.get(level, "Intermediate")
        keyboard = settings_main_menu(user_skill_level)
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Settings", reply_markup=reply_markup)

    elif query.data == 'cancel':
        await query.edit_message_text(text="Cancelled")   

@send_typing_action    
async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.edited_message or not update.message or update.message.via_bot:
        return

    user = update.effective_user
    logger.info(f"Received New Text Message User: {user.first_name} with ID: {user.id}")

    user_data = get_user(user.id)

    if not user_data["success"]:
        await context.bot.send_message(chat_id=user.id, text=log_and_return("get_user", user, user_data), parse_mode=ParseMode.HTML)
        return

    status_result = check_user_status(
        user_status=user_data["status"],
        is_bot=user_data["is_bot"],
        req_count=user_data["request_count"]
    )
    if not status_result["success"]:
        await context.bot.send_message(chat_id=user.id, text=log_and_return("check_user_status", user, status_result), parse_mode=ParseMode.HTML)
        return
    
    user_text = update.message.text
    user_text = user_text.strip()

    add_result = add_conversation(user.id, user_text, "user")
    if not add_result["success"]:
        await context.bot.send_message(chat_id=user.id, text=log_and_return("add_conversation", user, add_result), parse_mode=ParseMode.HTML)
        return
    
    conversations_result = get_conversations(user.id)
    if not conversations_result["success"]:
        await context.bot.send_message(chat_id=user.id, text=log_and_return("get_conversations", user, conversations_result), parse_mode=ParseMode.HTML)
        return
    #FIXME: check if there is no system promp then add it
    #TODO: Add summary = await summarize_user_conversations(user.id)
    # logger.info(f'conversations_result: {conversations_result["conversations"]}')
    tokens_count = count_tokens(conversations_result["conversations"])
    # logger.info(f'tokens_count: {tokens_count}')

    max_token = max_token_chat_free if user_data["status"] == 'zer' else max_token_chat

    query = conversations_result["conversations"]

    chat_result = await create_chat_completion(query, max_token)
    if not chat_result["success"]:
        await context.bot.send_message(chat_id=user.id, text=log_and_return("create_chat_completion", user, chat_result), parse_mode=ParseMode.HTML)
        return

    bot_response = chat_result["content"]
    logger.info(f'create_chat_completion_result: {user.first_name} with ID: {user.id}. message: {bot_response}\nToken; {chat_result["total_tokens"]}')

    credit_update_result = update_user_credit_req_count(user.id, user_data["credit"], user_data["request_count"], chat_result["total_tokens"])
    if not credit_update_result["success"]:
        await context.bot.send_message(chat_id=user.id, text=log_and_return("update_user_credit_req_count", user, credit_update_result), parse_mode=ParseMode.HTML)
        return

    add_result = add_conversation(user.id, bot_response, "assistant")
    if not add_result["success"]:
        await context.bot.send_message(chat_id=user.id, text=log_and_return("add_conversation", user, add_result), parse_mode=ParseMode.HTML)
        return

    # await context.bot.send_message(chat_id=user.id, text=chat_result["content"], parse_mode=ParseMode.HTML)
    await context.bot.send_message(chat_id=user.id, text=bot_response, parse_mode=ParseMode.HTML)