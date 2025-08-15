from fastapi import HTTPException,Depends
from config.snowflake import connection
import jwt
import datetime
import bcrypt
import sys
import os
import dotenv
dotenv.load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
            raise HTTPException(status_code=400, detail="Username already exists")
        else:
            hashed_password = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt())
            insert_query = "INSERT INTO PFT.USERS (username, email, password) VALUES (%s, %s, %s)"
            cursor.execute(insert_query, (user_data.username, user_data.email, hashed_password.decode('utf-8')))
            db.commit()
            cursor.close()
            return {
                "success": True,
                "message": "User registered successfully",
                "data": {
                    "username": user_data.username,
                    "email": user_data.email
                }
            }

    except HTTPException:
        raise
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
            return {
                "success": True,
                "message": "Login successful",
                "data": {
                    "user_id": user[0],
                    "username": user_data.username
                },
                "token": token
            }
        else:
            cursor.close()
            raise HTTPException(status_code=401, detail="Invalid credentials")

    except HTTPException:
        raise
    except Exception as e:
        print(type(e))
        raise HTTPException(status_code=500, detail=str(e))

def forgot_password(user_data):
    try:
        cursor = db.cursor()
        check_user_query = "SELECT * FROM PFT.USERS WHERE username = %s AND email = %s"
        cursor.execute(check_user_query, (user_data.username, user_data.email))
        user = cursor.fetchone()
        if user:
            if user_data.new_password:
                if bcrypt.checkpw(user_data.new_password.encode('utf-8'), user[3].encode('utf-8')):
                    raise HTTPException(status_code=400, detail="New password cannot be the same as the old password")
                hashed_password = bcrypt.hashpw(user_data.new_password.encode('utf-8'), bcrypt.gensalt())
                update_password_query = "UPDATE PFT.USERS SET password = %s WHERE username = %s"
                cursor.execute(update_password_query, (hashed_password.decode('utf-8'), user_data.username))
                db.commit()
                return {
                    "success": True,
                    "message": "Password updated successfully"
                }
            else:
                raise HTTPException(status_code=400, detail="Password is required")
        else:
            raise HTTPException(status_code=404, detail="Invalid Credentials")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()