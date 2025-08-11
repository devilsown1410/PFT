from fastapi import APIRouter
from controllers.auth import login as auth_login, register as auth_register
from models.auth import UserLogin, UserRegister

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
