import os
import sys
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dependencies import get_db_connection

class UserProfile(BaseModel):
    username: str
    email: str

router = APIRouter()


@router.get("/profile/{username}")
async def get_user_profile(username: str, db=Depends(get_db_connection)):
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
            return {"status_code": 200, "data": UserProfile(username=username,email=email)}

        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/profile/{username}")
async def update_user_profile(username: str, user_data: UserProfile, db=Depends(get_db_connection)):
    print(f"Updating profile for user: {username}")
    try:
        cursor = db.cursor()
        query = "UPDATE PFT.USERS SET email = %s WHERE username = %s"
        cursor.execute(query, (user_data.email, username))
        db.commit()
        cursor.close()
        if cursor.rowcount > 0:
            return {"status_code": 200, "data": UserProfile(username=username, email=user_data.email)}
        else:
            raise HTTPException(status_code=404, detail="User not found or no changes made")
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/profile/{username}")
async def delete_user_profile(username: str, db=Depends(get_db_connection)):
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
