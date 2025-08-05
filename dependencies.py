from fastapi import Depends
from config.snowflake import get_snowflake_connection

# This will be overridden in main.py with the actual connection
def get_db_connection():
    return get_snowflake_connection()
