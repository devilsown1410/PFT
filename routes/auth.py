from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import jwt
import datetime
import bcrypt
import sys
import os
import dotenv
dotenv.load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dependencies import get_db_connection

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

router = APIRouter()


@router.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application!"}

@router.post("/register")
def register(user_data: UserRegister, db=Depends(get_db_connection)):
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

@router.post("/login")
def login(user_data: UserLogin, db=Depends(get_db_connection)):
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

