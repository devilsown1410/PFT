from fastapi import HTTPException
from config.snowflake import connection
from utils import helper
global db
db = connection.get_connection()
def get_gcm(request, page, limit):
    try:
        user_id = request.state.current_user
        cursor = db.cursor()
        get_gcm_query = "SELECT TO_CHAR(UT.transaction_date, 'YYYY-MM'),C.name,SUM(UT.amount) AS month_expense FROM PFT.USER_TRANSACTIONS UT JOIN PFT.EXPENSE_CATEGORY C ON UT.category_id = C.id WHERE UT.user_id = %s AND UT.transaction_type='expense' GROUP BY TO_CHAR(UT.transaction_date, 'YYYY-MM'),C.name ORDER BY C.name;"
        cursor.execute(get_gcm_query, (user_id,))
        result = cursor.fetchall()
        cursor.close()
        return {"status_code": 200, "data": helper.pagination(result, page, limit)}
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

def get_gtbm(request, month):
    try:
        user_id = request.state.current_user
        cursor = db.cursor()
        get_gtbm_query = """
        SELECT TO_CHAR(UT.transaction_date, 'YYYY-MM') AS month,
        SUM(CASE WHEN UT.transaction_type= 'income' THEN UT.amount WHEN UT.transaction_type= 'expense' THEN -UT.amount ELSE 0 END) AS net_total,
        SUM(CASE WHEN UT.transaction_type= 'income' THEN UT.amount ELSE 0 END) AS total_income,
        SUM(CASE WHEN UT.transaction_type= 'expense' THEN UT.amount ELSE 0 END) AS total_expenses,
        COUNT(UT.id) AS transaction_count
        FROM PFT.USER_TRANSACTIONS UT
        WHERE UT.user_id = %s AND TO_CHAR(UT.transaction_date, 'YYYY-MM') = %s
        GROUP BY TO_CHAR(UT.transaction_date, 'YYYY-MM')
        ;"""
        cursor.execute(get_gtbm_query, (user_id, month))
        result = cursor.fetchone()
        cursor.close()
        if result:
            return {
                "status_code": 200,
                "data": {
                    "month": result[0],
                    "net_total": result[1],
                    "total_income": result[2],
                    "total_expenses": result[3],
                    "transaction_count": result[4]
                }
            }
        else:
            raise HTTPException(status_code=404, detail="No data found for the specified month")
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))