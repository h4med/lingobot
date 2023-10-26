import os
from typing import Dict

from dotenv import load_dotenv

load_dotenv()

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