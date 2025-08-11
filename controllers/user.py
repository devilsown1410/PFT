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
        print(f"User fetched: {user}")
        if user:

            username,email=user
            print(f"Returning user profile: {username}, {email}")
            return {"status_code": 200, "data": {"username": username, "email": email}}

        else:
            raise HTTPException(status_code=404, detail="User not found")
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
        cursor.close()
        if cursor.rowcount > 0:
            return {"status_code": 200, "data": {"username": username, "email": user_data.email}}
        else:
            raise HTTPException(status_code=404, detail="User not found or no changes made")
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
        cursor.close()
        if cursor.rowcount > 0:
            return {"status_code": 200, "detail": "User deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
