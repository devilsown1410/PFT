from fastapi import APIRouter,Request, Depends, HTTPException
from pydantic import BaseModel
import sys
import os
from dependencies import get_db_connection
from typing import Optional


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Budget(BaseModel):
    category_id: int
    month: str
    amount: float

class BudgetUpdate(BaseModel):
    category_id: Optional[int] = None
    month: Optional[str] = None
    amount: Optional[float] = None

router = APIRouter()

@router.post("/add")
def create_budget(budget: Budget, request: Request, db=Depends(get_db_connection)):
    try:
        user_id = request.state.current_user
        cursor = db.cursor()
        add_budget_query = "INSERT INTO PFT.BUDGET (user_id, category_id, budget_month, budget_amount) VALUES (%s, %s, %s, %s)"
        cursor.execute(add_budget_query, (user_id, budget.category_id, budget.month, budget.amount))
        db.commit()
        cursor.close()
        return {"status_code": 200, "detail": "Budget created successfully"}
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

@router.patch("/update/{budget_id}")
def update_budget(budget_id: int, budget: BudgetUpdate, request: Request, db=Depends(get_db_connection)):
    try:
        user_id = request.state.current_user
        cursor = db.cursor()
        check_budget_query = "SELECT * FROM PFT.BUDGET WHERE id = %s AND user_id = %s"
        cursor.execute(check_budget_query, (budget_id, user_id))
        print(f"Checking budget with ID {budget_id} for user {user_id}")
        existing_budget = cursor.fetchone()
        if not existing_budget:
            raise HTTPException(status_code=404, detail="Budget not found")
        if existing_budget[3] != user_id:
            raise HTTPException(status_code=403, detail="You are not authorized to update this budget")
        update_budget_query = "UPDATE PFT.BUDGET SET category_id = %s, budget_month = %s, budget_amount = %s WHERE id = %s AND user_id = %s"
        cursor.execute(update_budget_query, (budget.category_id, budget.month, budget.amount, budget_id, user_id))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Budget not found or no changes made")
        
        print(f"Updated budget with ID {budget_id} for user {user_id}")
        db.commit()
        cursor.close()
        return {"status_code": 200, "detail": "Budget updated successfully"}
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

