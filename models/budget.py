from pydantic import BaseModel
from typing import Optional
class Budget(BaseModel):
    category_id: int
    month: str
    amount: float

class BudgetUpdate(BaseModel):
    category_id: Optional[int] = None
    month: Optional[str] = None
    amount: Optional[float] = None