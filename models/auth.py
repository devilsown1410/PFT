from pydantic import BaseModel
class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class ForgotPassword(BaseModel):
    username: str
    email: str
    new_password: str