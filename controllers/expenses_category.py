from fastapi import HTTPException
from config.snowflake import connection
from utils import helper
global db
db = connection.get_connection()
def create_expense_category(expense, request):
    try:
        user_id=request.state.current_user
        check_existing_query = "SELECT * FROM PFT.EXPENSE_CATEGORY WHERE name = %s AND user_id = %s"
        cursor=db.cursor()
        cursor.execute(check_existing_query, (expense.name, user_id))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Expense Category already exists")
        else:
            add_expense_query = "INSERT INTO PFT.EXPENSE_CATEGORY (name, user_id) VALUES (%s, %s)"
            cursor.execute(add_expense_query, (expense.name, user_id))
            db.commit()
            cursor.close()
            return {"status_code":200,"detail":"Expense Category added Successfully"}
    
    except Exception as e:
        print(f"Error occured: {str(e)}")
        raise HTTPException(status_code=500,detail=str(e))

def edit_expense_category(expense, request):
    try:
        if(request.state.current_user != expense.user_id):
            raise HTTPException(status_code=403, detail="You are not authorized to edit this expense category")
        else:
            cursor=db.cursor()
            id= request.path_params['id']
            edit_expense_query= "UPDATE PFT.EXPENSE_CATEGORY SET (name, user_id) = (%s, %s) WHERE id = %s"
            cursor.execute(edit_expense_query, (expense.name, expense.user_id, id))
            db.commit()
            cursor.close()
            return {"status_code":200,"detail":"Expense Category updated Successfully"}

    except Exception as e:
        print(f"Error occured: {str(e)}")
        raise HTTPException(status_code=500,detail=str(e))

def delete_expense_category(request):
    try:
        id = request.path_params['id']
        if(request.state.current_user != id):
            raise HTTPException(status_code=403, detail="You are not authorized to delete this expense category")
        else:
            cursor= db.cursor()
            delete_expense_query = "DELETE FROM PFT.EXPENSE_CATEGORY WHERE id = %s"
            cursor.execute(delete_expense_query, (id,))
            db.commit()
            cursor.close()
            return {"status_code":200,"detail":"Expense Category deleted Successfully"}
    except Exception as e:
        print(f"Error occured: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def list_expense_categories(request, page: int = 1, limit: int = 10):
    try:
        user_id= request.state.current_user
        cursor = db.cursor()
        list_expense_query = "SELECT id, name FROM PFT.EXPENSE_CATEGORY WHERE user_id = %s"
        cursor.execute(list_expense_query, (user_id,))
        expenses = cursor.fetchall()
        cursor.close()
        return {"status_code": 200, "data": helper.pagination(expenses, page, limit)}
    except Exception as e:
        print(f"Error occured: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def get_expense_category(id, request):
    try:
        get_expense_query = "SELECT id, name FROM PFT.EXPENSE_CATEGORY WHERE id = %s"
        cursor = db.cursor()
        cursor.execute(get_expense_query, (id,))
        expense = cursor.fetchone()
        cursor.close()
        if not expense:
            raise HTTPException(status_code=404, detail="Expense Category not found")
        return {"status_code": 200, "data": expense}
    except Exception as e:
        print(f"Error occured: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    