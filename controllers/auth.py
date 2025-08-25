from fastapi import HTTPException,Depends
from config.snowflake import async_db_manager
import jwt
import datetime
import bcrypt
import sys
import os
import dotenv
dotenv.load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def register(user_data):
    try:
        # Check if user already exists
        check_user_query = "SELECT * FROM PFT.USERS WHERE username = %s"
        user = await async_db_manager.execute_query_one_async(check_user_query, (user_data.username,))
        
        if user:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Hash password and insert new user
        hashed_password = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt())
        insert_query = "INSERT INTO PFT.USERS (username, email, password) VALUES (%s, %s, %s)"
        await async_db_manager.execute_command_async(
            insert_query, 
            (user_data.username, user_data.email, hashed_password.decode('utf-8'))
        )
        
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

async def login(user_data):
    try:
        print("Attempting to log in user:", user_data.username)
        check_user_query = "SELECT id,username, password FROM PFT.USERS WHERE username = %s"
        user = await async_db_manager.execute_query_one_async(check_user_query, (user_data.username,))

        if user and bcrypt.checkpw(user_data.password.encode('utf-8'), user[2].encode('utf-8')):
            payload = {
                'user_id': user[0],
                'username': user_data.username,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }
            token = jwt.encode(payload, os.environ["secret_key"], algorithm='HS256')

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
            raise HTTPException(status_code=401, detail="Invalid credentials")

    except HTTPException:
        raise
    except Exception as e:
        print(type(e))
        raise HTTPException(status_code=500, detail=str(e))

async def forgot_password(user_data):
    try:
        check_user_query = "SELECT * FROM PFT.USERS WHERE username = %s AND email = %s"
        user = await async_db_manager.execute_query_one_async(check_user_query, (user_data.username, user_data.email))
        
        if user:
            if user_data.new_password:
                if bcrypt.checkpw(user_data.new_password.encode('utf-8'), user[3].encode('utf-8')):
                    raise HTTPException(status_code=400, detail="New password cannot be the same as the old password")
                
                hashed_password = bcrypt.hashpw(user_data.new_password.encode('utf-8'), bcrypt.gensalt())
                update_password_query = "UPDATE PFT.USERS SET password = %s WHERE username = %s"
                await async_db_manager.execute_command_async(
                    update_password_query, 
                    (hashed_password.decode('utf-8'), user_data.username)
                )
                
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