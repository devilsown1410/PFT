from dotenv import load_dotenv
from routes.app import app
import uvicorn

def main():
    load_dotenv()
    uvicorn.run("routes.app:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()  