# app/modules/openai_api.py

import openai
import tiktoken
import os
from dotenv import load_dotenv
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    retry_if_exception_type
) 

from app.log_config import configure_logging
from app.helpers.utils import download_audio_file

load_dotenv()
openai.api_key = os.environ['OPENAI_API_KEY']

logger = configure_logging(__name__)

#TODO: add Retries with exponential backoff 
# https://platform.openai.com/docs/guides/rate-limits/error-mitigation
# https://learn.microsoft.com/en-us/dotnet/architecture/microservices/implement-resilient-applications/implement-retries-exponential-backoff

@retry(
    retry=retry_if_exception_type(openai.error.RateLimitError),
    wait=wait_random_exponential(min=4, max=60),
    stop=stop_after_attempt(5),
    reraise=True
)
async def create_chat_completion(messages_list, max_token, response_format = "text", model="gpt-3.5-turbo-1106", temperature=0.3):
    try:
        logger.info("Starting OpenAI ChatCompletion...")
        response = await openai.ChatCompletion.acreate(
            model=model,
            max_tokens=max_token,
            response_format={ "type": response_format },
            messages=messages_list,
            temperature=temperature
        )
        logger.info(f"OpenAI ChatCompletion done with total tokens: {response['usage']['total_tokens']}")
        return {
                    "success": True, 
                    "message": "Response received.", 
                    "content": response.choices[0].message["content"], 
                    "prompt_tokens":response['usage']['prompt_tokens'], 
                    "completion_tokens": response['usage']['completion_tokens'], 
                    "total_tokens": response['usage']['total_tokens']
                }
    
    except openai.error.RateLimitError  as e:
        logger.error(f"RateLimitError Error: {e}")
        return {
            "success": False, 
            "message": f"RateLimitError Error: {e}", 
            "content":"Bot is Busy, please try again in a minute or two."
            }
    except openai.error.InvalidRequestError as e:
        logger.error(f"InvalidRequestError Error: {e}")
        return {"success": False, "message": f"InvalidRequestError Error: {e}"}
    except Exception as e:
        logger.error(f"Exception Error: {e}")
        return {"success": False, "message": f"An Exception occurred: {e}"}
    

def count_tokens(messages) -> int:
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens_per_message = 3
    tokens_per_name = 1
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            if value is not None:
                num_tokens += len(encoding.encode(str(value)))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens

async def get_audio_file_transcription(voice_file, voice_file_id, voice_file_duration, lang='en'):
    result  = await download_audio_file(voice_file, voice_file_id)

    if not result['success']:
        return {"success": False, "message": f"Error: {result['message']}"}
    
    voice_wav = result['voice_wav']
    logger.info(f'Audio received for transcription with length: {str(voice_file_duration)} seconds.')

    try:
        transcript = await openai.Audio.atranscribe(
            model="whisper-1", 
            file=voice_wav,
            language=lang
            )
        transcription = transcript["text"]
        logger.info(f"openai atranscribe done with transcription length of: {len(transcription)}")
        return {
                    "success": True, 
                    "message": "Response received.", 
                    "content": transcription
                }
    
    except openai.error.RateLimitError  as e:
        logger.error(f"RateLimitError Error: {e}")
        return {"success": False, "message": f"RateLimitError Error: {e}", "content":"Bot is Busy, please try again in a minute or two."}
    except openai.error.InvalidRequestError as e:
        logger.error(f"InvalidRequestError Error: {e}")
        return {"success": False, "message": f"InvalidRequestError Error: {e}"}
    except Exception as e:
        logger.error(f"Exception Error: {e}")
        return {"success": False, "message": f"An Exception occurred: {e}"}

    return 