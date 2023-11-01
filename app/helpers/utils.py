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
        # oga_temp_file = tempfile.NamedTemporaryFile(suffix='.oga', delete=False)
        # wav_temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        
        # await voice_file.download(voice_file_id + ".oga")  # Assuming this downloads the file locally
        
        # with open(voice_file_id + ".oga", "rb") as f:
        #     voice = AudioSegment.from_ogg(f)

        # voice.export(wav_temp_file.name, format="wav")
        # wav_temp_file.seek(0)
        # voice_wav = wav_temp_file.read()

        # # Cleanup temporary files
        # os.remove(voice_file_id + ".oga")
        # wav_temp_file.close()  # This will also delete the temporary wav file due to delete=True (default)

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
        # Cleanup in case of an error
        if os.path.exists(voice_file_id + ".oga"):
            os.remove(voice_file_id + ".oga")
        wav_temp_file.close()  # This will also delete the temporary wav file due to delete=True (default)

        return {
            "success": False,
            "message": f"An error occurred: {e}"
        }
