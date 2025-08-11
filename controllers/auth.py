from fastapi import HTTPException,Depends
from pydantic import BaseModel
from config.snowflake import connection
import jwt
import datetime
import bcrypt
import sys
import os
import dotenv
dotenv.load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

global db
db = connection.get_connection()

def register(user_data):
    try:
        cursor = db.cursor()
        check_user_query = "SELECT * FROM PFT.USERS WHERE username = %s"
        cursor.execute(check_user_query, (user_data.username,))
        user = cursor.fetchone()
        
        if user:
            cursor.close()
            return {"status_code": 400, "detail": "Username already exists"}
        else:
            hashed_password = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt())
            insert_query = "INSERT INTO PFT.USERS (username, email, password) VALUES (%s, %s, %s)"
            cursor.execute(insert_query, (user_data.username, user_data.email, hashed_password.decode('utf-8')))
            db.commit()
            print("Transaction committed successfully!")
            cursor.close()
            return {"status_code": 200, "detail": "User registered successfully"}

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    

def login(user_data):
    try:
        cursor = db.cursor()
        check_user_query = "SELECT id,username, password FROM PFT.USERS WHERE username = %s"
        cursor.execute(check_user_query, (user_data.username,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(user_data.password.encode('utf-8'), user[2].encode('utf-8')):
            payload = {
                'user_id': user[0],
                'username': user_data.username,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }
            token = jwt.encode(payload, os.environ["secret_key"], algorithm='HS256')

            cursor.close()
            return {"status_code": 200, "detail": "Login successful", "token": token}
        else:
            cursor.close()
            return {"status_code": 401, "detail": "Invalid credentials"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
