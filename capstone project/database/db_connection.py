# database/db_connection.py

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """
    Returns a connection to the PostgreSQL database using .env credentials.
    """
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "program"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASS", "112233"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
    )
