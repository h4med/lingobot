# app/db_manager.py
import psycopg2
import logging
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def connect_to_db():
    try:
        connection = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
        return connection
    
    except Exception as e:
        logging.error(f'Calling connect_to_db, error occurred:\n{e} ')
        return None