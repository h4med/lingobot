# app/modules/google_tts.py

import os
import tempfile
import asyncio
import aiofiles
from google.cloud import texttospeech
import google.cloud.texttospeech as tts

from app.log_config import configure_logging

from dotenv import load_dotenv

load_dotenv()
google_api_key = os.environ['GOOGLE_API_KEY']
google_project_id = os.environ['GOOGLE_PROJECT_ID']

logger = configure_logging(__name__)

voice_names_dict= {
    # 'en': 'en-US-Standard-B',
    'en': 'en-US-Wavenet-D',
    'de': 'de-DE-Standard-B',
    'fr': 'fr-FR-Standard-B',
    'ar': 'ar-XA-Standard-B',
    'sv': 'sv-SE-Standard-D'
}

async def google_text_to_speak(text, lang='en'):
    try:    
        voice_name = voice_names_dict[lang]
        def synthesize_speech():
            text_input = tts.SynthesisInput(text=text)
            voice_params = tts.VoiceSelectionParams(
                language_code=lang, name=voice_name
            )

            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            client = tts.TextToSpeechClient(
                client_options={"api_key": google_api_key, "quota_project_id": google_project_id}
            )
            response = client.synthesize_speech(
                input=text_input,
                voice=voice_params,
                audio_config=audio_config,
            )

            return response

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, synthesize_speech)

        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file_name = f"{temp_file.name}.mp3"
        temp_file.close()

        async with aiofiles.open(temp_file_name, "wb") as out:
            await out.write(response.audio_content)
            logger.info(f'Audio content written to file "{temp_file_name}"')

        return {"success": True, "message": "Audio file created successfully.", "file_path": temp_file_name}
    
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return {"success": False, "message": f"An error occurred: {str(e)}"}