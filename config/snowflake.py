import snowflake.connector
import os
def get_snowflake_connection():
    try:
        connection_parameters={
            'user':os.environ['user'],
            'password':os.environ['chabi'],
            'account':os.environ['account'],
            'role':os.environ['role'],
            'warehouse':os.environ['warehouse'],
            'database':os.environ['database'],
            'schema':os.environ['schema'],
        }
        session=snowflake.connector.connect(**connection_parameters)
        print("Connection established successfully!")
        return session  
    except snowflake.connector.errors.OperationalError as e:
        print(f"Operational Error: {e}")
    except KeyError as e:
        print(f"Missing environment variable: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return None

class DatabaseManager:
    def __init__(self):
        self.connection = get_snowflake_connection()
        if self.connection is None:
            raise Exception("Failed to establish database connection")
        self._connection = self.connection

    def get_connection(self):
        if self._connection is None:
            self._connection = get_snowflake_connection()
        return self._connection
    
    def close_connection(self):
        """
        Closes the database connection (use only when shutting down the application)
        """ 
        if self._connection:
            self._connection.close()
            self._connection = None
            print("Database connection closed.")

connection= DatabaseManager()