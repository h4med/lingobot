# app/modules/message_processing.py
# User Message Management (app/modules/message_processing.py):
#     DONE: add_conversation(user_id, message, sent_by):
#     DONE: get_conversations(user_id, limit=20)
#     DONE: delete_conversations(user_id)
import os
from dotenv import load_dotenv
import psycopg2
from app.db_manager import connect_to_db
from app.helpers.utils import log_and_return
from app.messages.prompts import system_prompt, user_new_conv_start
from app.modules.user_management import create_user, get_user, update_user_credit_req_count, update_user_settings
from app.modules.openai_api import create_chat_completion, count_tokens
from app.log_config import configure_logging

load_dotenv()

logger = configure_logging(__name__)

max_token_chat = int(os.environ['CHATCOMPLETION_MAX_TOKEN'])
max_token_chat_free = int(os.environ['CHATCOMPLETION_MAX_TOKEN_FREE'])
max_token_summarize = int(os.environ['CHATCOMPLETION_MAX_TOKEN_SUMMARIZE'])


def add_conversation(user_id, message, sent_by):
    if not user_id or not isinstance(user_id, int) or user_id <= 0:
        return {"success": False, "message": "Invalid input: user_id is required and must be a positive integer."}    

    message = message.strip() if message else message
    sent_by = sent_by.strip().lower() if sent_by else sent_by

    if not message or not isinstance(message, str):
        return {"success": False, "message": "Invalid input: message is required and must be a non-empty string."}
    if sent_by not in ['user', 'system', 'assistant']:
        return {"success": False, "message": "Invalid input: sent_by must be either 'user' or 'assistant' or 'system'."}

    connection = connect_to_db()
    if connection is None:
        return {"success": False, "message": "Database connection failed."}

    try:
        with connection.cursor() as cursor:
            query = """
                INSERT INTO lingo_conversations (
                    user_id, 
                    message, 
                    sent_by, 
                    timestamp
                ) 
                VALUES (%s, %s, %s, NOW());
            """
            cursor.execute(query, (user_id, message, sent_by))
        connection.commit()
        return {"success": True, "message": "Conversation added successfully."}
    except psycopg2.Error as e:
        connection.rollback()
        return {"success": False, "message": f"An error occurred: {e}"}
    finally:
        connection.close()

def get_conversations(user_id, limit=1000):
    if not user_id or not isinstance(user_id, int) or user_id <= 0:
        return {"success": False, "message": "Invalid input: user_id is required and must be a positive integer."}
    if not isinstance(limit, int) or limit <= 0:
        return {"success": False, "message": "Invalid input: limit must be a positive integer."}

    connection = connect_to_db()
    if connection is None:
        return {"success": False, "message": "Database connection failed."}

    try:
        with connection.cursor() as cursor:
            query = """
                SELECT message, sent_by, timestamp
                FROM lingo_conversations
                WHERE user_id = %s
                ORDER BY timestamp ASC
                LIMIT %s;
            """
            cursor.execute(query, (user_id, limit))
            conversations = cursor.fetchall()
        
        result = [{
            "role": conversation[1],
            "content": conversation[0]
            # "timestamp": conversation[2]
        } for conversation in conversations]

        return {"success": True, "conversations": result}

    except psycopg2.Error as e:
        connection.rollback()
        return {"success": False, "message": f"An error occurred: {e}"}
    finally:
        connection.close()

def delete_conversations(user_id):
    if not user_id or not isinstance(user_id, int) or user_id <= 0:
        return {"success": False, "message": "Invalid input: user_id is required and must be a positive integer."}
    
    connection = connect_to_db()
    if connection is None:
        return {"success": False, "message": "Database connection failed."}
    
    try:
        with connection.cursor() as cursor:
            query = """
                DELETE FROM lingo_conversations
                WHERE user_id = %s;
            """
            cursor.execute(query, (user_id,))
        connection.commit()
        return {"success": True, "message": "Conversations deleted successfully."}
    
    except psycopg2.Error as e:
        connection.rollback()
        return {"success": False, "message": f"An error occurred: {e}"}
    
    finally:
        connection.close()

def init_conversations(user, user_data):

    prompt = system_prompt.format(user_name=user_data["first_name"], user_skill_level=user_data["level"])
    # start_msg = user_new_conv_start.format(user_skill_level=user_data["level"])
    start_msg = user_new_conv_start.format(user_name=user_data["first_name"], user_skill_level=user_data["level"])

    add_result = add_conversation(user.id, prompt, "system")
    if not add_result["success"]:
        return {"success": False, "message": log_and_return("add_conversation", user, add_result)}

    max_token = max_token_chat_free if user_data["status"] == 'zer' else max_token_chat

    query = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": start_msg}
    ]

    return {"success": True, "query": query, "max_token": max_token}

async def new_msg_process(user, user_data, user_msg, role="user"):

    add_result = add_conversation(user.id, user_msg, role)
    if not add_result["success"]:
        return {"success": False, "message": log_and_return("add_conversation", user, add_result)}
    
    conversations_result = get_conversations(user.id)
    if not conversations_result["success"]:
        return {"success": False, "message": log_and_return("get_conversations", user, conversations_result)}

    conversations = conversations_result["conversations"]
    if not conversations or conversations[0]["role"] != "system":
        #there is no user conversation or somthing is wrong!
        delete_conversations(user.id)
        init_conversations(user, user_data)
        add_conversation(user.id, user_msg, role)
        conversations_result = get_conversations(user.id)
        conversations = conversations_result["conversations"]


    tokens_count = count_tokens(conversations)

    if tokens_count > max_token_summarize:
        logger.info(f'Chat history for user ID {user.id} is too long! tokens_count: {tokens_count}, Summarising...')
        #TODO implement summary = await summarize_user_conversations(user.id)


    max_token = max_token_chat_free if user_data["status"] == 'zer' else max_token_chat

    chat_result = await create_chat_completion(conversations, max_token)
    if not chat_result["success"]:
        return {"success": False, "message": log_and_return("create_chat_completion", user, chat_result)}

    bot_response = chat_result["content"]
    logger.info(f'create_chat_completion_result: {user.first_name} with ID: {user.id}. message: {bot_response}\nToken; {chat_result["total_tokens"]}')

    credit_update_result = update_user_credit_req_count(user.id, user_data["credit"], user_data["request_count"], chat_result["total_tokens"])
    if not credit_update_result["success"]:
        return {"success": False, "message": log_and_return("update_user_credit_req_count", user, credit_update_result)}        

    add_result = add_conversation(user.id, bot_response, "assistant")
    if not add_result["success"]:
        return {"success": False, "message": log_and_return("add_conversation", user, add_result)}

    return {"success": True, "message": bot_response}