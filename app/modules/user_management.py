# app/modules/user_management.py
# User Management
# DONE create_user(user_id, first_name, last_name=None, username=None)
# TODO get_user(user_id)
# Returns all settings/status of user
# TODO update_user_credit_rq_count(user_id, credit, rq_count, credit_usage, rq_count_inc=1)
# returns new_credit, new_rq_count
# TODO increase_user_credit(user_id, credit_to_add)
# returns new_credit
# TODO update_user_model(user_id, model)
# returns success
# TODO get_user_settings(user_id)
# returns user model and level
# update_user_status(connection, user_id, status)
# delete_user(connection, user_id)
# log_user_activity(connection, user_id, activity_type, tokens, duration)
# get_user_logs(connection, user_id, start_date=None, end_date=None, activity_type=None)
# delete_user_logs(connection, user_id, timestamp=None)

import psycopg2
from app.db_manager import connect_to_db

def create_user(user_id, first_name, last_name=None, username=None):
    # Input validation
    if not first_name or not isinstance(first_name, str):
        return {"success": False, "message": "Invalid input: first_name is required and must be a non-empty string."}
    
    connection = connect_to_db()
    if connection is None:
        return {"success": False, "message": "Database connection failed."}

    try:
        with connection.cursor() as cursor:
            query = """
                INSERT INTO lingo_users (
                    user_id, 
                    first_name, 
                    last_name, 
                    username, 
                    joined_at
                ) 
                VALUES (%s, %s, %s, %s, NOW());
            """
            cursor.execute(query, (user_id, first_name, last_name, username))
        connection.commit()
        return {"success": True, "message": "User created successfully."}
    except psycopg2.Error as e:
        connection.rollback()
        return {"success": False, "message": f"An error occurred: {e}"}
    finally:
        connection.close()

def get_user(user_id):
    if not user_id:
        return {"success": False, "message": "Invalid input: user_id is required."}
    
    connection = connect_to_db()
    if connection is None:
        return {"success": False, "message": "Database connection failed."}

    try:
        with connection.cursor() as cursor:
            query = """
                SELECT first_name, status, credit, level, model, request_count 
                FROM lingo_users 
                WHERE user_id = %s;
            """
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            
            if result is None:
                return {"success": False, "message": "User not found."}
            else:
                return {
                    "success": True, 
                    "message": "User found.", 
                    "first_name": result[0], 
                    "status": result[1], 
                    "credit": result[2], 
                    "level": result[3], 
                    "model": result[4],
                    "request_count": result[5]
                }
    except psycopg2.Error as e:
        connection.rollback()
        return {"success": False, "message": f"An error occurred: {e}"}
    finally:
        connection.close()