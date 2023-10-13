# app/modules/user_management.py
# User Management
# DONE create_user(user_id, first_name, last_name=None, username=None)
# DONE get_user(user_id)
# Returns all settings/status of user
# DONE update_user_credit_req_count(user_id, credit, req_count, usage, req_count_inc=1)
# returns new_credit, new_req_count
# TODO increase_user_credit(user_id, credit_to_add)
# returns new_credit
# TODO update_user_model(user_id, model)
# returns success
# TODO get_user_settings(user_id)
# returns user model and level
# TODO update_user_status(connection, user_id, status)
# delete_user(connection, user_id)
# TODO log_user_activity(connection, user_id, activity_type, tokens, duration)
# TODO get_user_logs(connection, user_id, start_date=None, end_date=None, activity_type=None)
# delete_user_logs(connection, user_id, timestamp=None)

import psycopg2
from app.db_manager import connect_to_db

def create_user(user_id, first_name, last_name=None, username=None):
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
                SELECT first_name, last_name, username, status, credit, level, model, request_count 
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
                    "last_name": result[1], 
                    "username": result[2], 
                    "status": result[3], 
                    "credit": result[4], 
                    "level": result[5], 
                    "model": result[6],
                    "request_count": result[7]
                }
    except psycopg2.Error as e:
        connection.rollback()
        return {"success": False, "message": f"An error occurred: {e}"}
    finally:
        connection.close()

def update_user_credit_req_count(user_id, credit, req_count, usage, req_count_inc=1):

    if not user_id:
        return {"success": False, "message": "Invalid input: user_id is required."}
    
    if not isinstance(credit, int) or credit < 0:
        return {"success": False, "message": "Invalid input: credit must be a non-negative integer."}

    if not isinstance(req_count, int) or req_count < 0:
        return {"success": False, "message": "Invalid input: req_count must be a non-negative integer."}

    if not isinstance(usage, int) or usage < 0:
        return {"success": False, "message": "Invalid input: usage must be a non-negative integer."}

    if not isinstance(req_count_inc, int) or req_count_inc < 0:
        return {"success": False, "message": "Invalid input: req_count_inc must be a non-negative integer."}
    
    connection = connect_to_db()
    if connection is None:
        return {"success": False, "message": "Database connection failed."}
    
    try:
        with connection.cursor() as cursor:
            new_credit = 0
            new_status = 'zer'
            if credit > usage:
                new_credit = credit - usage
                new_status = 'ena'
                    
            new_req_count = req_count + req_count_inc            
            query = """
                UPDATE lingo_users SET 
                request_count = %s, 
                credit = %s, 
                status = %s 
                WHERE user_id = %s
            """
            cursor.execute(query, (new_req_count, new_credit, new_status, user_id))
        connection.commit()
        return {
            "success": True, 
            "message": "User credit and req count updated.", 
            "new_credit": new_credit, 
            "new_req_count": new_req_count
                }
    except psycopg2.Error as e:
        connection.rollback()
        return {"success": False, "message": f"An error occurred: {e}"}
    finally:
        connection.close() 

