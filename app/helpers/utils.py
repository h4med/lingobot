import os
from typing import Dict
from pydub import AudioSegment
import tempfile

from dotenv import load_dotenv
from app.log_config import configure_logging

load_dotenv()

logger = configure_logging(__name__)

daily_quota_free = int(os.environ['DAILY_QUOTA_FREE'])
daily_quota_max = int(os.environ['DAILY_QUOTA_MAX'])

from telegram import Update, Message
from telegram.ext import ContextTypes

async def send_temp_message(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str = "[Processing...]") -> int:
    temp_message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text
    )
    return temp_message.message_id

async def delete_message(update: Update, context: ContextTypes.DEFAULT_TYPE, message_id: int):
    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=message_id
    )

def check_user_status(user_status, is_bot, req_count):

    if user_status == 'zer' and req_count >= daily_quota_free:
        return {"success": False, "message": "Sorry, No Credit and No free Quota, please check your blaance /balance"} #TODO: add messages to messages/responses.py
    elif user_status == 'dis':
        return {"success": False, "message": "Sorry, The user is disabled"}
    elif req_count >= daily_quota_max:
        return {"success": False, "message": "Sorry, Max quota exhausted!"} #TODO: add better messages to messages/responses.py
    elif is_bot:
        return {"success": False, "message": "Sorry, You are BOT!"}

    return {"success": True, "message": "No problem, continue"}

def log_and_return(action: str, user, _result: Dict):
    message = _result["message"]
    logger.error(f'{action}: {user.first_name} with ID: {user.id}. Error: {message}')
    return message

async def download_audio_file(voice_file, voice_file_id):
    try:
        await voice_file.download_to_drive(voice_file_id + ".oga")

        with open(voice_file_id + ".oga", "rb") as f:
            voice = AudioSegment.from_ogg(f)
        voice_wav = voice.export(voice_file_id + ".wav", format="wav")
        
        os.remove(voice_file_id + ".oga")
        os.remove(voice_file_id + ".wav")

        return {
            "success": True,
            "message": "Audio file downloaded and converted successfully.",
            "voice_wav": voice_wav
        }
    except Exception as e:
        if os.path.exists(voice_file_id + ".oga"):
            os.remove(voice_file_id + ".oga")
        return {
            "success": False,
            "message": f"An error occurred: {e}"
        }
