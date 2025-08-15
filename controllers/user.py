from fastapi import HTTPException
from config.snowflake import connection
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
        query = "UPDATE PFT.USERS SET email = %s WHERE username = %s"
        cursor.execute(query, (user_data.email, username))
        db.commit()
        affected_rows = cursor.rowcount
        cursor.close()
        if affected_rows > 0:
            return {
                "success": True,
                "message": "User profile updated successfully",
                "data": {
                    "username": username,
                    "email": user_data.email
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
