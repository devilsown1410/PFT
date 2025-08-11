from fastapi import HTTPException
from config.snowflake import connection
global db
db = connection.get_connection()
def create_budget(budget, request):
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

def update_budget(budget_id, budget, request):
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

        update_fields = []
        update_values = []
        
        if budget.category_id is not None:
            update_fields.append("category_id = %s")
            update_values.append(budget.category_id)
        
        if budget.month is not None:
            update_fields.append("budget_month = %s")
            update_values.append(budget.month)
        
        if budget.amount is not None:
            update_fields.append("budget_amount = %s")
            update_values.append(budget.amount)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields provided for update")
        
        update_budget_query = f"UPDATE PFT.BUDGET SET {', '.join(update_fields)} WHERE id = %s AND user_id = %s"
        update_values.extend([budget_id, user_id])
        cursor.execute(update_budget_query, tuple(update_values))
        
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