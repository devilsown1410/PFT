from fastapi import APIRouter,Request, Depends, HTTPException
from pydantic import BaseModel
import sys
import os
from datetime import datetime
from dependencies import get_db_connection
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

router = APIRouter()

@router.post("/add")
def create_transaction(transaction: Transaction, request: Request, db=Depends(get_db_connection)):
    try:
        user_id = request.state.current_user
        cursor = db.cursor()
        print(transaction.transaction_date[:7])
        if transaction.transaction_type not in ['income', 'expense']:
            raise HTTPException(status_code=400, detail="Invalid transaction type")
        budget_check_query = "SELECT budget_amount FROM PFT.BUDGET WHERE user_id = %s AND category_id = %s AND budget_month = %s"
        cursor.execute(budget_check_query, (user_id, transaction.category_id, transaction.transaction_date[:7]))
        budget = cursor.fetchone()
        print(f"Budget fetched: {budget}")
        if not budget:
            raise HTTPException(status_code=400, detail="Budget not found")
        check_availability_query = "SELECT SUM(amount) FROM PFT.USER_TRANSACTIONS WHERE user_id = %s AND category_id = %s AND TO_CHAR(transaction_date, 'YYYY-MM') = %s"
        cursor.execute(check_availability_query, (user_id, transaction.category_id, transaction.transaction_date[:7]))

        print(f"Checking availability for user {user_id} in category {transaction.category_id} for month {transaction.transaction_date[:7]}")
        availability = cursor.fetchone()
        print(f"Availability fetched: {availability}")
        availability= float(availability[0]) if availability[0] is not None else 0.0
        print(f"Availability: {availability}")
        global alert
        alert = ''
        if availability and transaction.transaction_type == 'expense' and (availability + transaction.amount) > budget[0]:
            percentage= (availability + transaction.amount) / float(budget[0]) * 100
            print(f"Percentage of budget used: {percentage}")
            if percentage>=80 and percentage<90:
                alert = f"You have crossed 80% of your budget."
            elif percentage>=90 and percentage<100:
                alert = f"You have crossed 90% of your budget."
            elif percentage>=100:
                alert = f"You have crossed 100% of your budget."
        print("do ndf")
        if transaction.transaction_date:
            date_obj = datetime.strptime(transaction.transaction_date, "%Y-%m-%d")
        print(f"Adding transaction: {transaction.amount}, {transaction.description}, {transaction.category_id}, {user_id}, {transaction.transaction_type}, {date_obj.strftime('%Y-%m-%d')}")
        add_transaction_query = "INSERT INTO PFT.USER_TRANSACTIONS (amount, description, category_id, user_id, transaction_type, transaction_date) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(add_transaction_query, (transaction.amount, transaction.description, transaction.category_id, user_id, transaction.transaction_type, date_obj))
        db.commit()
        cursor.close()
        if alert:
            return {"status_code": 200, "detail": "Transaction added successfully", "alert": alert}
        else:
            return {"status_code": 200, "detail": "Transaction added successfully"}
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

@router.put("/update/{transaction_id}")
def update_transaction(transaction_id: int, transaction: TransactionUpdate, request: Request, db=Depends(get_db_connection)):
    try:
        user_id = request.state.current_user
        cursor = db.cursor()
        check_transaction_query = "SELECT * FROM PFT.USER_TRANSACTIONS WHERE id = %s AND user_id = %s"
        cursor.execute(check_transaction_query, (transaction_id, user_id))
        existing_transaction = cursor.fetchone()
        if not existing_transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        if existing_transaction.user_id != user_id:
            raise HTTPException(status_code=403, detail="You are not authorized to update this transaction")
        update_transaction_query = "UPDATE PFT.USER_TRANSACTIONS SET amount = %s, description = %s, category_id = %s, transaction_type = %s, transaction_date = %s WHERE id = %s AND user_id = %s"
        cursor.execute(update_transaction_query, (transaction.amount, transaction.description, transaction.category_id, transaction.transaction_type, transaction.transaction_date, transaction_id, user_id))
        db.commit()
        cursor.close()
        return {"status_code": 200, "detail": "Transaction updated successfully"}
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

@router.delete("/delete/{transaction_id}")
def delete_transaction(transaction_id: int, request: Request, db=Depends(get_db_connection)):
    try:
        user_id = request.state.current_user
        cursor=db.cursor()
        check_transaction_query = "SELECT * FROM PFT.USER_TRANSACTIONS WHERE id = %s AND user_id = %s"
        cursor.execute(check_transaction_query, (transaction_id, user_id))
        existing_transaction = cursor.fetchone()
        if not existing_transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        if existing_transaction.user_id != user_id:
            raise HTTPException(status_code=403, detail="You are not authorized to delete this transaction")
        delete_transaction_query = "DELETE FROM PFT.USER_TRANSACTIONS WHERE id = %s AND user_id = %s"
        cursor.execute(delete_transaction_query, (transaction_id, user_id))
        db.commit()
        cursor.close()
        return {"status_code": 200, "detail": "Transaction deleted successfully"}
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

@router.get("/list")
def list_transactions(request: Request, db=Depends(get_db_connection)):
    try:
        user_id = request.state.current_user
        cursor = db.cursor()
        list_transactions_query= "SELECT * FROM PFT.USER_TRANSACTIONS WHERE user_id = %s"
        cursor.execute(list_transactions_query, (user_id,))
        transactions = cursor.fetchall()
        cursor.close()
        return {"status_code": 200, "data": transactions}
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

@router.get("/get/{transaction_id}")
def get_transaction(transaction_id: int, request: Request, db=Depends(get_db_connection)):
    try:
        user_id = request.state.current_user
        cursor = db.cursor()
        get_transaction_query = "SELECT * FROM PFT.USER_TRANSACTIONS WHERE id = %s AND user_id = %s"
        cursor.execute(get_transaction_query, (transaction_id, user_id))
        transaction = cursor.fetchone()
        cursor.close()
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return {"status_code": 200, "data": transaction}
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

