# app/modules/user_management.py
# User Management
# TODO update_user_settings(user_id, level, model)
# returns sucess
# TODO get_user_settings(user_id)
# returns user model and level
# TODO increase_user_credit(user_id, credit_to_add)
# returns new_credit
# TODO update_user_model(user_id, model)
# returns success
# TODO update_user_status(connection, user_id, status)
# delete_user(connection, user_id)
# TODO log_user_activity(connection, user_id, activity_type, tokens, duration)
# TODO get_user_logs(connection, user_id, start_date=None, end_date=None, activity_type=None)
# delete_user_logs(connection, user_id, timestamp=None)

import psycopg2
from app.db_manager import connect_to_db

def create_user(user_id, first_name, is_bot, last_name=None, username=None):
    if not first_name or not isinstance(first_name, str) or not isinstance(is_bot, bool):
        return {"success": False, "message": "app/modules/user_management.py - create_user() - Invalid input"}
    
    connection = connect_to_db()
    if connection is None:
        return {"success": False, "message": "app/modules/user_management.py - create_user() - Database connection failed."}

    try:
        with connection.cursor() as cursor:
            # Check if user already exists
            check_query = """
                SELECT 1 FROM lingo_users WHERE user_id = %s;
            """
            cursor.execute(check_query, (user_id,))
            if cursor.fetchone():
                return {"success": False, "message": "User already exists"}

            # If not, proceed to insert new user
            insert_query = """
                INSERT INTO lingo_users (
                    user_id, 
                    first_name, 
                    last_name, 
                    username, 
                    is_bot,
                    joined_at
                ) 
                VALUES (%s, %s, %s, %s, %s, NOW());
            """
            cursor.execute(insert_query, (user_id, first_name, last_name, username, is_bot))
        connection.commit()
        return {"success": True, "message": "User created successfully."}
    except psycopg2.Error as e:
        connection.rollback()
        return {"success": False, "message": f"app/modules/user_management.py - create_user() - An error occurred: {e}"}
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
                SELECT first_name, last_name, username, is_bot, status, credit, level, model, request_count 
                FROM lingo_users 
                WHERE user_id = %s;
            """
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            
            if result is None:
                return {"success": False, "message": "User not found."}
            else:
                level_map = {
                    "1": "beginner",
                    "2": "elementary",
                    "3": "intermediate",
                    "4": "upper-intermediate",
                    "5": "advanced",
                }
                user_skill_level=level_map.get(str(result[6]), "Intermediate")
                return {
                    "success": True, 
                    "message": "User found.", 
                    "first_name": result[0], 
                    "last_name": result[1], 
                    "username": result[2], 
                    "is_bot": result[3], 
                    "status": result[4], 
                    "credit": result[5], 
                    "level": user_skill_level, 
                    "model": result[7],
                    "request_count": result[8]
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


def update_user_settings(user_id, level, model="GPT-3.5"):
    if not user_id or not isinstance(user_id, int) or user_id <= 0:
        return {"success": False, "message": "Invalid input: user_id is required and must be a positive integer."}
    if not level or not isinstance(level, int) or level <= 0:
        return {"success": False, "message": "Invalid input: level is required and must be a positive integer."}
    if not model or not isinstance(model, str):
        return {"success": False, "message": "Invalid input: model is required and must be a non-empty string."}

    connection = connect_to_db()
    if connection is None:
        return {"success": False, "message": "Database connection failed."}

    try:
        with connection.cursor() as cursor:
            query = """
                UPDATE lingo_users 
                SET level = %s, model = %s 
                WHERE user_id = %s;
            """
            cursor.execute(query, (level, model, user_id))
        connection.commit()
        return {
            "success": True,
            "message": "User settings updated successfully.",
            "level": level,
            "model": model
        }
    except psycopg2.Error as e:
        connection.rollback()
        return {"success": False, "message": f"An error occurred: {e}"}
    finally:
        connection.close()
