# scripts/clear_table.py

import sys
import psycopg2
from app.db_manager import connect_to_db

def clear_table(table_name):
    connection = connect_to_db()
    if connection is None:
        print("Database connection failed.")
        return

    try:
        with connection.cursor() as cursor:
            query = f"TRUNCATE TABLE {table_name} CASCADE;"
            cursor.execute(query)
        connection.commit()
        print(f'Table {table_name} and all referencing tables cleared successfully.')
    except psycopg2.Error as e:
        connection.rollback()
        print(f"An error occurred: {e}")
    finally:
        connection.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 clear_table.py <table_name>")
    else:
        table_name = sys.argv[1]
        clear_table(table_name)
