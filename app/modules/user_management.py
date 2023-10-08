# app/modules/user_management.py

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
