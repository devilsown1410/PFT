from dotenv import load_dotenv
from config.snowflake import get_snowflake_connection
from routes.app import app
from dependencies import get_db_connection
import uvicorn

def main():
    load_dotenv()
    connect = get_snowflake_connection()
    app.dependency_overrides[get_db_connection] = lambda: connect
    uvicorn.run("routes.app:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()