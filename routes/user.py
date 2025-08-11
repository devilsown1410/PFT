import os
import sys
from fastapi import APIRouter
from models.user import UserProfile
from controllers.user import (
    get_user_profile as get_user_profile_controller,
    update_user_profile as update_user_profile_controller,
    delete_user_profile as delete_user_profile_controller
)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

router = APIRouter()

@router.get("/profile/{username}")
async def get_user_profile(username: str):
    print(f"Fetching profile for user: {username}")
    return await get_user_profile_controller(username)

@router.put("/profile/{username}")
async def update_user_profile(username: str, user_data: UserProfile):
    print(f"Updating profile for user: {username}")
    return await update_user_profile_controller(username, user_data)
    
@router.delete("/profile/{username}")
async def delete_user_profile(username: str):
    print(f"Deleting profile for user: {username}")
    return await delete_user_profile_controller(username)
