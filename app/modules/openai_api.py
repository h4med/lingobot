# app/modules/openai_api.py

import openai
import tiktoken
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.environ['OPENAI_API_KEY']

from app.log_config import configure_logging

logger = configure_logging(__name__)

async def create_chat_completion(messages_list, max_token, model="gpt-3.5-turbo-16k", temperature=0.3):

    try:
        response = await openai.ChatCompletion.acreate(
            model=model,
            messages=messages_list,
            temperature=temperature,
            max_tokens=max_token
        )
        logger.info(f"openai ChatCompletion done with total tokens: {response['usage']['total_tokens']}")
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
        return {"success": False, "message": f"RateLimitError Error: {e}", "content":"Bot is Busy, please try again in a minute or two."}
    except openai.error.InvalidRequestError as e:
        logger.error(f"InvalidRequestError Error: {e}")
        return {"success": False, "message": f"InvalidRequestError Error: {e}"}
    except Exception as e:
        logger.error(f"Exception Error: {e}")
        return {"success": False, "message": f"An Exception occurred: {e}"}