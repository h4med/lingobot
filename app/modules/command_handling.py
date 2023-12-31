# app/modules/command_handling.py

import os
from dotenv import load_dotenv
from functools import wraps

from telegram import InlineKeyboardMarkup, Update

from telegram.ext import (
    ContextTypes
)
from telegram.constants import ChatAction, ParseMode

from app.modules.user_management import create_user, get_user, update_user_credit_req_count, update_user_settings
from app.modules.message_processing import delete_conversations, init_conversations, new_msg_process, format_feedback, remove_html_tags
from app.modules.openai_api import create_chat_completion, get_audio_file_transcription
from app.modules.google_tts import google_text_to_speak
from app.messages.responses import start_message, start_message_back
from app.messages.menu import settings_main_menu, settings_level_list_menu
from app.log_config import configure_logging
from app.helpers.utils import check_user_status, log_and_return, send_temp_message, delete_message

logger = configure_logging(__name__)

load_dotenv()

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

async def handle_credit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user 
    logger.info(f'Received /credit first_name: {user.first_name}')

    user_data = get_user(user.id)

    if not user_data["success"]:
        await context.bot.send_message(chat_id=user.id, text=log_and_return("get_user", user, user_data), parse_mode=ParseMode.HTML)
        return
    
    first_name = user_data["first_name"]
    status = user_data["status"]
    credit = user_data["credit"]
    request_count = user_data["request_count"]
    
    text = f"""Dear <b>{first_name}</b>,

Credit: {credit}
Request Count: {request_count}
Status: {status}

@ChatGPTSpeackBot
    """
    await context.bot.send_message(
    chat_id=update.effective_chat.id, 
    text=text,
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
    
    processing_messge_id = await send_temp_message(update, context, text="[Please wait...]")

    deletion_result = delete_conversations(user.id)
    if not deletion_result["success"]:
        await context.bot.send_message(chat_id=user.id, text=log_and_return("delete_conversations", user, deletion_result), parse_mode=ParseMode.HTML)
        return
    
    init_conversations_result = init_conversations(user, user_data)
    if not init_conversations_result["success"]:
        await context.bot.send_message(chat_id=user.id, text=log_and_return("init_conversations", user, init_conversations_result), parse_mode=ParseMode.HTML)
        return

    max_token = init_conversations_result["max_token"]
    query = init_conversations_result["query"]

    chat_result = await create_chat_completion(query, max_token, "json_object", "gpt-3.5-turbo-1106", 0.7)
    if not chat_result["success"]:
        await context.bot.send_message(chat_id=user.id, text=log_and_return("create_chat_completion", user, chat_result), parse_mode=ParseMode.HTML)
        return

    credit_update_result = update_user_credit_req_count(user.id, user_data["credit"], user_data["request_count"], chat_result["total_tokens"])
    if not credit_update_result["success"]:
        await context.bot.send_message(chat_id=user.id, text=log_and_return("update_user_credit_req_count", user, credit_update_result), parse_mode=ParseMode.HTML)
        return

    await delete_message(update, context, message_id=processing_messge_id)

    formatted_text = format_feedback(chat_result["content"])
    if not formatted_text["success"]:
        await context.bot.send_message(chat_id=user.id, text=log_and_return("formatted_text", user, formatted_text), parse_mode=ParseMode.HTML)
        return

    await context.bot.send_message(chat_id=user.id, text=formatted_text["message"], parse_mode=ParseMode.HTML)

    # text_for_tts = remove_html_tags(formatted_text["message"])

    # logger.info(f'formatted_text: {formatted_text["message"]}\ntext_for_tts: {text_for_tts}')

    google_tts_result = await google_text_to_speak(chat_result["content"])
    if not google_tts_result["success"]:
        await context.bot.send_message(chat_id=user.id, text=log_and_return("google_text_to_speak", user, google_tts_result), parse_mode=ParseMode.HTML)
        return

    await context.bot.send_voice(chat_id=update.effective_chat.id, voice=google_tts_result["file_path"])

    return

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
    
    processing_messge_id = await send_temp_message(update, context, text="[Processing...]") 

    user_msg = update.message.text
    user_msg = user_msg.strip()

    new_msg_process_result = await new_msg_process(user, user_data, user_msg, "user")

    if not new_msg_process_result["success"]:
        await context.bot.send_message(chat_id=user.id, text=log_and_return("new_msg_process", user, new_msg_process_result), parse_mode=ParseMode.HTML)
        return

    await context.bot.delete_message(
        chat_id=user.id,
        message_id=processing_messge_id
    )
    
    await context.bot.send_message(chat_id=user.id, text=new_msg_process_result["message"], parse_mode=ParseMode.HTML)

    google_tts_result = await google_text_to_speak(new_msg_process_result["message"])
    if not google_tts_result["success"]:
        await context.bot.send_message(chat_id=user.id, text=log_and_return("google_text_to_speak", user, google_tts_result), parse_mode=ParseMode.HTML)
        return

    await context.bot.send_voice(chat_id=update.effective_chat.id, voice=google_tts_result["file_path"])

    return

@send_voice_action
async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.edited_message or not update.message or update.message.via_bot:
        return
    
    user = update.effective_user
    logger.info(f"Received New Voice Message User: {user.first_name} with ID: {user.id}")

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

    transcribing_messge_id = await send_temp_message(update, context, text="[Transcribing, please wait...]") 

    file_id = update.message.voice.file_id
    duration  = update.message.voice.duration
    voice_file =  await context.bot.get_file(file_id, read_timeout=30)

    get_transcription_result = await get_audio_file_transcription(voice_file, file_id, duration)
    if not get_transcription_result["success"]:
        await context.bot.send_message(chat_id=user.id, text=log_and_return("get_transcription_result", user, user_data), parse_mode=ParseMode.HTML)
        return
    
    user_msg = get_transcription_result["content"]
    user_msg = user_msg.strip()

    await delete_message(update, context, message_id=transcribing_messge_id)

    await context.bot.send_message(chat_id=user.id, text=f"[🗣 <i>{user_msg}</i>]", parse_mode=ParseMode.HTML)
    
    processing_messge_id = await send_temp_message(update, context, text="[Processing...]") 

    new_msg_process_result = await new_msg_process(user, user_data, user_msg, "user")

    if not new_msg_process_result["success"]:
        await context.bot.send_message(chat_id=user.id, text=log_and_return("new_msg_process", user, new_msg_process_result), parse_mode=ParseMode.HTML)
        return

    await delete_message(update, context, message_id=processing_messge_id)

    await context.bot.send_message(chat_id=user.id, text=new_msg_process_result["message"], parse_mode=ParseMode.HTML)

    # print(new_msg_process_result["message"])
    # print(remove_html_tags(new_msg_process_result["message"]))
    google_tts_result = await google_text_to_speak(remove_html_tags(new_msg_process_result["message"]))
    if not google_tts_result["success"]:
        await context.bot.send_message(chat_id=user.id, text=log_and_return("google_text_to_speak", user, google_tts_result), parse_mode=ParseMode.HTML)
        return

    await context.bot.send_voice(chat_id=update.effective_chat.id, voice=google_tts_result["file_path"])

    return


