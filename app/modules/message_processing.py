# app/modules/message_processing.py
# User Message Management (app/modules/message_processing.py):
#     DONE: add_conversation(user_id, message, sent_by):
#     DONE: get_conversations(user_id, limit=20)
#     DONE: delete_conversations(user_id)

import psycopg2
from app.db_manager import connect_to_db

def add_conversation(user_id, message, sent_by):
    if not user_id or not isinstance(user_id, int) or user_id <= 0:
        return {"success": False, "message": "Invalid input: user_id is required and must be a positive integer."}    

    message = message.strip() if message else message
    sent_by = sent_by.strip().lower() if sent_by else sent_by

    if not message or not isinstance(message, str):
        return {"success": False, "message": "Invalid input: message is required and must be a non-empty string."}
    if sent_by not in ['user', 'bot']:
        return {"success": False, "message": "Invalid input: sent_by must be either 'user' or 'bot'."}

    connection = connect_to_db()
    if connection is None:
        return {"success": False, "message": "Database connection failed."}

    try:
        # Inserting conversation record
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

def get_conversations(user_id, limit=20):
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
                ORDER BY timestamp DESC
                LIMIT %s;
            """
            cursor.execute(query, (user_id, limit))
            conversations = cursor.fetchall()
        
        result = [{
            "message": conversation[0],
            "sent_by": conversation[1],
            "timestamp": conversation[2]
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
