from fastapi import APIRouter
from controllers.auth import login as auth_login, register as auth_register, forgot_password as auth_forgot_password
from models.auth import UserLogin, UserRegister, ForgotPassword

router = APIRouter()


@router.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI application!"}

@router.post("/register")
async def register_user(user_data: UserRegister):
    return await auth_register(user_data)

@router.post("/login")
async def login_user(user_data: UserLogin):
    return await auth_login(user_data)

@router.patch("/forgot-password")
async def forgot_password(user_data: ForgotPassword):
    return await auth_forgot_password(user_data)
