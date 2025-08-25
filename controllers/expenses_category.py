from fastapi import HTTPException
from config.snowflake import async_db_manager
from utils import helper

async def create_expense_category(expense, request):
    try:
        user_id = request.state.current_user
        
        # Check if expense category already exists
        check_existing_query = "SELECT * FROM PFT.EXPENSE_CATEGORY WHERE name = %s AND user_id = %s"
        existing = await async_db_manager.execute_query_one_async(check_existing_query, (expense.name, user_id))
        
        if existing:
            raise HTTPException(status_code=409, detail="Expense Category already exists")
        
        # Create new expense category
        add_expense_query = "INSERT INTO PFT.EXPENSE_CATEGORY (name, user_id) VALUES (%s, %s)"
        await async_db_manager.execute_command_async(add_expense_query, (expense.name, user_id))
        
        return {
            "status_code": 201,
            "detail": "Expense Category created successfully",
            "data": {
                "name": expense.name,
                "user_id": user_id
            }
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def edit_expense_category(expense, request):
    try:
        id = request.path_params['id']
        
        if request.state.current_user != expense.user_id:
            raise HTTPException(status_code=403, detail="You are not authorized to edit this expense category")
        
        edit_expense_query = "UPDATE PFT.EXPENSE_CATEGORY SET name = %s, user_id = %s WHERE id = %s"
        affected_rows = await async_db_manager.execute_command_async(
            edit_expense_query, 
            (expense.name, expense.user_id, id)
        )
        
        if affected_rows == 0:
            raise HTTPException(status_code=404, detail="Expense category not found")
            
        return {
            "status_code": 200,
            "detail": "Expense Category updated successfully",
            "data": {
                "id": id,
                "name": expense.name,
                "user_id": expense.user_id
            }
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def delete_expense_category(request):
    try:
        id = request.path_params['id']
        user_id = request.state.current_user
        
        # Check if expense category exists and belongs to user
        check_query = "SELECT user_id FROM PFT.EXPENSE_CATEGORY WHERE id = %s"
        expense_category = await async_db_manager.execute_query_one_async(check_query, (id,))
        
        if not expense_category:
            raise HTTPException(status_code=404, detail="Expense category not found")
            
        if expense_category[0] != user_id:
            raise HTTPException(status_code=403, detail="You are not authorized to delete this expense category")
        
        delete_expense_query = "DELETE FROM PFT.EXPENSE_CATEGORY WHERE id = %s"
        await async_db_manager.execute_command_async(delete_expense_query, (id,))
        
        return {
            "status_code": 200,
            "detail": "Expense Category deleted successfully"
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def list_expense_categories(request, page, limit):
    try:
        user_id = request.state.current_user
        list_expense_query = "SELECT id, name FROM PFT.EXPENSE_CATEGORY WHERE user_id = %s ORDER BY id LIMIT %s OFFSET %s"
        expenses = await async_db_manager.execute_query_async(
            list_expense_query, 
            (user_id, limit, (page - 1) * limit)
        )
        
        return {
            "success": True,
            "message": "Expense categories retrieved successfully",
            "data": list(map(lambda x: {"id": x[0], "name": x[1]}, expenses))
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def get_expense_category(id, request):
    try:
        user_id = request.state.current_user
        get_expense_query = "SELECT id, name FROM PFT.EXPENSE_CATEGORY WHERE id = %s AND user_id = %s"
        expense = await async_db_manager.execute_query_one_async(get_expense_query, (id, user_id))
        
        if not expense:
            raise HTTPException(status_code=404, detail="Expense Category not found")
            
        return {
            "status_code": 200,
            "data": {
                "id": expense[0],
                "name": expense[1]
            }
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    