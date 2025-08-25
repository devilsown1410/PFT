from fastapi import HTTPException
from config.snowflake import async_db_manager

async def create_budget(budget, request):
    try:
        user_id = request.state.current_user
        add_budget_query = "INSERT INTO PFT.BUDGET (user_id, category_id, budget_month, budget_amount) VALUES (%s, %s, %s, %s)"
        await async_db_manager.execute_command_async(
            add_budget_query, 
            (user_id, budget.category_id, budget.month, budget.amount)
        )
        
        return {
            "success": True,
            "message": "Budget created successfully",
            "data": {
                "user_id": user_id,
                "category_id": budget.category_id,
                "month": budget.month,
                "amount": f"${budget.amount}"
            }
        }
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def update_budget(budget_id, budget, request):
    try:
        user_id = request.state.current_user
        
        # Check if budget exists and belongs to user
        check_budget_query = "SELECT * FROM PFT.BUDGET WHERE id = %s AND user_id = %s"
        existing_budget = await async_db_manager.execute_query_one_async(check_budget_query, (budget_id, user_id))
        
        if not existing_budget:
            raise HTTPException(status_code=404, detail="Budget not found")
            
        if existing_budget[3] != user_id:
            raise HTTPException(status_code=403, detail="You are not authorized to update this budget")

        # Build dynamic update query
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
        
        affected_rows = await async_db_manager.execute_command_async(update_budget_query, tuple(update_values))
        
        if affected_rows == 0:
            raise HTTPException(status_code=404, detail="Budget not found or no changes made")
        
        return {
            "success": True,
            "message": "Budget updated successfully",
            "data": {
                "budget_id": budget_id,
                "category_id": budget.category_id,
                "month": budget.month,
                "amount": f"${budget.amount}"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def list_budgets(request, page=1, limit=10):
    try:
        user_id = request.state.current_user
        list_budgets_query = "SELECT * FROM PFT.BUDGET WHERE user_id = %s ORDER BY budget_month LIMIT %s OFFSET %s"
        offset = (page - 1) * limit
        budgets = await async_db_manager.execute_query_async(list_budgets_query, (user_id, limit, offset))
        
        return {
            "success": True,
            "message": "Budgets retrieved successfully",
            "data": list(map(lambda x: {
                "id": x[0],
                "month": x[1],
                "amount": f"${x[2]}",
                "category_id": x[4]
            }, budgets))
        }
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
