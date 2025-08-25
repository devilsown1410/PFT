from contextlib import asynccontextmanager, contextmanager
import asyncio
import concurrent.futures
from threading import Lock
import os
from typing import AsyncGenerator, Optional
import logging
from snowflake import connector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_snowflake_connection():
    try:
        connection_parameters = {
            'user': os.environ['user'],
            'password': os.environ['chabi'],
            'account': os.environ['account'],
            'role': os.environ['role'],
            'warehouse': os.environ['warehouse'],
            'database': os.environ['database'],
            'schema': os.environ['schema'],
        }
        session = connector.connect(**connection_parameters)
        logger.info("Connection established successfully!")
        return session
    except connector.errors.OperationalError as e:
        logger.error(f"Operational Error: {e}")
        return None
    except KeyError as e:
        logger.error(f"Missing environment variable: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None

class AsyncDatabaseManager:
    def __init__(self, max_workers: int = 10):
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self._lock = Lock()
    async def get_connection_async(self) -> Optional[object]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._executor, get_snowflake_connection)
    
    @asynccontextmanager
    async def get_connection_context(self) -> AsyncGenerator[object, None]:
        connection = None
        try:
            connection = await self.get_connection_async()
            if connection is None:
                raise Exception("Failed to establish database connection")
            yield connection
        finally:
            if connection:
                try:
                    connection.close()
                    logger.info("Database connection closed in context manager")
                except Exception as e:
                    logger.error(f"Error closing connection: {e}")
    
    @asynccontextmanager
    async def get_cursor_context(self) -> AsyncGenerator[tuple, None]:
        async with self.get_connection_context() as connection:
            cursor = None
            try:
                cursor = connection.cursor()
                yield connection, cursor
            finally:
                if cursor:
                    try:
                        cursor.close()
                        logger.debug("Database cursor closed")
                    except Exception as e:
                        logger.error(f"Error closing cursor: {e}")
    
    async def execute_query_async(self, query: str, params: tuple = None) -> list:
        async with self.get_cursor_context() as (connection,cursor):
            loop = asyncio.get_event_loop()
            
            def execute():
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                return cursor.fetchall()
            return await loop.run_in_executor(self._executor, execute)

    async def execute_query_one_async(self, query: str, params: tuple = None) -> tuple:
        async with self.get_cursor_context() as (connection,cursor):
            loop = asyncio.get_event_loop()
            def execute():
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                return cursor.fetchone()
            
            return await loop.run_in_executor(self._executor, execute)
    
    async def execute_command_async(self, query: str, params: tuple = None) -> int:
        async with self.get_cursor_context() as (connection, cursor):
            loop = asyncio.get_event_loop()
            
            def execute():
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                connection.commit()
                return cursor.rowcount
            
            return await loop.run_in_executor(self._executor, execute)    
    def cleanup(self):
        self._executor.shutdown(wait=True)
async_db_manager = AsyncDatabaseManager()