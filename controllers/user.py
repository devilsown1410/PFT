from fastapi import HTTPException
from config.snowflake import connection
import bcrypt
db = connection.get_connection()
async def get_user_profile(username):
    print(f"Fetching profile for user: {username}")
    try:
        cursor= db.cursor()
        query = "SELECT username as username, email as email FROM PFT.USERS WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        cursor.close()
        if user:
            username, email = user
            print(f"Returning user profile: {username}, {email}")
            return {
                "success": True,
                "message": "User profile retrieved successfully",
                "data": {
                    "username": username,
                    "email": email
                }
            }

        else:
            raise HTTPException(status_code=404, detail="User not found")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
async def update_user_profile(username, user_data):
    print(f"Updating profile for user: {username}")
    try:
        cursor = db.cursor()
        update_fields = []
        update_values = []
        
        if user_data.email is not None:
            update_fields.append("email = %s")
            update_values.append(user_data.email)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields provided for update")
        
        update_values.append(username)
        query = f"UPDATE PFT.USERS SET {', '.join(update_fields)} WHERE username = %s"
        
        cursor.execute(query, tuple(update_values))
        db.commit()
        affected_rows = cursor.rowcount
        cursor.close()        
        if affected_rows > 0:
            cursor = db.cursor()
            cursor.execute("SELECT username, email FROM PFT.USERS WHERE username = %s", (username,))
            user = cursor.fetchone()
            cursor.close()
            
            return {
                "success": True,
                "message": "User profile updated successfully",
                "data": {
                    "username": user[0],
                    "email": user[1]
                }
            }
        else:
            raise HTTPException(status_code=404, detail="User not found or no changes made")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
async def delete_user_profile(username):
    print(f"Deleting profile for user: {username}")
    try:
        cursor = db.cursor()
        query = "DELETE FROM PFT.USERS WHERE username = %s"
        cursor.execute(query, (username,))
        db.commit()
        affected_rows = cursor.rowcount
        cursor.close()
        if affected_rows > 0:
            return {
                "success": True,
                "message": "User deleted successfully",
                "data": {
                    "username": username
                }
            }
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def update_user_password(request, username, new_password):
    try:
        user_id = request.state.current_user
        cursor = db.cursor()
        if not new_password:
            raise HTTPException(status_code=400, detail="New password is required")
        user_query = "SELECT * FROM PFT.USERS WHERE id = %s"
        cursor.execute(user_query, (user_id,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user[1] != username:
            raise HTTPException(status_code=403, detail="You are not authorized to update this user's password")
        if bcrypt.checkpw(new_password.encode('utf-8'), user[3].encode('utf-8')):
            raise HTTPException(status_code=400, detail="New password cannot be the same as the old password")
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        update_query = "UPDATE PFT.USERS SET password = %s WHERE id = %s"
        cursor.execute(update_query, (hashed_password.decode('utf-8'), user_id))
        db.commit()
        cursor.close()
        return {
            "success": True,
            "message": "Password updated successfully",
            "data": {
                "username": username
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()