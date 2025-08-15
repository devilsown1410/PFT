from fastapi import APIRouter
from controllers.auth import login as auth_login, register as auth_register, forgot_password as auth_forgot_password
from models.auth import UserLogin, UserRegister, ForgotPassword

router = APIRouter()


@router.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application!"}

@router.post("/register")
def register_user(user_data: UserRegister):
    return auth_register(user_data)

@router.post("/login")
def login_user(user_data: UserLogin):
    return auth_login(user_data)

@router.patch("/forgot-password")
def forgot_password(user_data: ForgotPassword):
    return auth_forgot_password(user_data)
