from pydantic import BaseModel
from typing import Optional
class Transaction(BaseModel):
    amount: float
    description: str
    category_id: int
    transaction_type: str
    transaction_date: str

class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    transaction_type: Optional[str] = None
    transaction_date: Optional[str] = None

class SearchQuery(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    transaction_type: Optional[str] = None
    category_id: Optional[int] = None