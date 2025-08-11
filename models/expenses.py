from pydantic import BaseModel
class Expense(BaseModel):
    name: str