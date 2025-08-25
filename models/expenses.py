from pydantic import BaseModel
from typing import Optional

class Expense(BaseModel):
    name: str
    user_id: Optional[int] = None