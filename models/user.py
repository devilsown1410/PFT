from pydantic import BaseModel
from typing import Optional

class UserProfile(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None