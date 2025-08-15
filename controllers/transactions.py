from fastapi import HTTPException
from utils import helper
from config.snowflake import connection
from datetime import datetime, timezone
global db
db = connection.get_connection()
def create_transaction(transaction, request):
    try:
        user_id = request.state.current_user
        cursor = db.cursor()
        transaction_date = datetime.now(timezone.utc).isoformat()
        if transaction.transaction_type not in ['income', 'expense']:
            raise HTTPException(status_code=400, detail="Invalid transaction type")
        budget_check_query = "SELECT budget_amount FROM PFT.BUDGET WHERE user_id = %s AND category_id = %s AND budget_month = %s"
        cursor.execute(budget_check_query, (user_id, transaction.category_id, transaction_date[:7]))
        budget = cursor.fetchone()
        if not budget:
            raise HTTPException(status_code=400, detail="Budget not found")
        check_availability_query = "SELECT SUM(amount) FROM PFT.USER_TRANSACTIONS WHERE user_id = %s AND category_id = %s AND TO_CHAR(transaction_date, 'YYYY-MM') = %s"
        cursor.execute(check_availability_query, (user_id, transaction.category_id, transaction_date[:7]))
        availability = cursor.fetchone()
        
        availability= float(availability[0]) if availability[0] is not None else 0.0
        
        global alert
        alert = ''
        if availability and transaction.transaction_type == 'expense' and (availability + transaction.amount) > budget[0]:
            percentage= (availability + transaction.amount) / float(budget[0]) * 100
            
            if percentage>=80 and percentage<90:
                alert = f"You have crossed 80% of your budget."
            elif percentage>=90 and percentage<100:
                alert = f"You have crossed 90% of your budget."
            elif percentage>=100:
                alert = f"You have crossed 100% of your budget."
        add_transaction_query = "INSERT INTO PFT.USER_TRANSACTIONS (amount, description, category_id, user_id, transaction_type, transaction_date) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(add_transaction_query, (transaction.amount, transaction.description, transaction.category_id, user_id, transaction.transaction_type, transaction_date))
        db.commit()
        cursor.close()
        
        response = {
            "success": True,
            "message": "Transaction added successfully",
            "data": {
                "amount": f"${transaction.amount}",
                "description": transaction.description,
                "category_id": transaction.category_id,
                "transaction_type": transaction.transaction_type,
                "transaction_date": transaction_date
            }
        }
        
        if alert:
            response["alert"] = alert
            
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

def update_transaction(transaction_id, transaction, request):
    try:
        user_id = request.state.current_user
        cursor = db.cursor()
        check_transaction_query = "SELECT * FROM PFT.USER_TRANSACTIONS WHERE id = %s AND user_id = %s"
        cursor.execute(check_transaction_query, (transaction_id, user_id))
        existing_transaction = cursor.fetchone()
        if not existing_transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        if existing_transaction[5] != user_id:
            raise HTTPException(status_code=403, detail="You are not authorized to update this transaction")
        update_fields = []
        update_values = []
        if transaction.amount is not None:
            update_fields.append("amount = %s")
            update_values.append(transaction.amount)
        if transaction.description is not None:
            update_fields.append("description = %s")
            update_values.append(transaction.description)
        if transaction.category_id is not None:
            update_fields.append("category_id = %s")
            update_values.append(transaction.category_id)
        if transaction.transaction_type is not None:
            if transaction.transaction_type not in ['income', 'expense']:
                raise HTTPException(status_code=400, detail="Invalid transaction type")
            update_fields.append("transaction_type = %s")
            update_values.append(transaction.transaction_type)
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields provided for update")
        
        update_transaction_query = f"UPDATE PFT.USER_TRANSACTIONS SET {', '.join(update_fields)} WHERE id = %s AND user_id = %s"
        update_values.append(transaction_id)
        update_values.append(user_id)
        cursor.execute(update_transaction_query, tuple(update_values))
        db.commit()
        cursor.close()
        return {
            "success": True,
            "message": "Transaction updated successfully",
            "data": {
                "transaction_id": transaction_id,
                "amount": f"${transaction.amount}",
                "description": transaction.description,
                "category_id": transaction.category_id,
                "transaction_type": transaction.transaction_type,
                "transaction_date": existing_transaction[6]
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

def delete_transaction(transaction_id, request):
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
        return {
            "success": True,
            "message": "Transaction deleted successfully",
            "data": {
                "transaction_id": transaction_id
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

def list_transactions(request, page: int = 1, limit: int = 10):
    try:
        user_id = request.state.current_user
        cursor = db.cursor()
        list_transactions_query= "SELECT * FROM PFT.USER_TRANSACTIONS WHERE user_id = %s ORDER BY transaction_date DESC LIMIT %s OFFSET %s"
        cursor.execute(list_transactions_query, (user_id, limit, (page - 1) * limit))
        transactions = cursor.fetchall()
        cursor.close()
        return {
            "success": True,
            "message": "Transactions retrieved successfully",
            "data": helper.transaction_response(transactions)
        }
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

def get_transaction(transaction_id, request):
    try:
        user_id = request.state.current_user
        cursor = db.cursor()
        get_transaction_query = "SELECT * FROM PFT.USER_TRANSACTIONS WHERE id = %s AND user_id = %s"
        cursor.execute(get_transaction_query, (transaction_id, user_id))
        transaction = cursor.fetchone()
        cursor.close()
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return {
            "success": True,
            "message": "Transaction retrieved successfully",
            "data": helper.transaction_response(transaction)
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

def search_transactions(field, search_query, request, page: int = 1, limit: int = 10):
    try:
        user_id = request.state.current_user
        cursor = db.cursor()
        if field == "transaction_type":
            if not search_query.transaction_type:
                raise HTTPException(status_code=400, detail="Transaction type is required for type search")
            if search_query.transaction_type not in ['income', 'expense']:
                raise HTTPException(status_code=400, detail="Invalid transaction type")
            cursor.execute("SELECT * FROM PFT.USER_TRANSACTIONS WHERE user_id = %s AND transaction_type = %s LIMIT %s OFFSET %s", (user_id, search_query.transaction_type,limit, (page - 1) * limit))
        elif field == "category":
            if not search_query.category_id:
                raise HTTPException(status_code=400, detail="Category ID is required for category search")
            cursor.execute("SELECT * FROM PFT.USER_TRANSACTIONS WHERE user_id = %s AND category_id = %s LIMIT %s OFFSET %s", (user_id, search_query.category_id, limit, (page - 1) * limit))
        elif field == "date":
            if not search_query.start_date or not search_query.end_date:
                raise HTTPException(status_code=400, detail="Start date and end date are required for date search")
            cursor.execute("SELECT * FROM PFT.USER_TRANSACTIONS WHERE user_id = %s AND transaction_date BETWEEN %s AND %s LIMIT %s OFFSET %s", (user_id, search_query.start_date, search_query.end_date, limit, (page - 1) * limit))
        else:
            raise HTTPException(status_code=400, detail="Invalid search field")
        results = cursor.fetchall()
        cursor.close()
        return {
            "success": True,
            "message": "Transactions retrieved successfully",
            "data": helper.transaction_response(results)
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()  
