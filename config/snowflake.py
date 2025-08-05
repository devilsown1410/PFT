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
