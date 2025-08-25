from fastapi import HTTPException
from config.snowflake import async_db_manager
from utils import helper

async def get_gcm(request, page, limit):
    try:
        user_id = request.state.current_user
        get_gcm_query = """
        SELECT 
            TO_CHAR(UT.transaction_date, 'YYYY-MM') AS month,
            C.name AS category,
            SUM(UT.amount) AS month_expense,
            B.budget_amount,
            CASE 
                WHEN SUM(UT.amount) > B.budget_amount THEN 'Budget Exceeded'
                WHEN SUM(UT.amount) > (B.budget_amount * 0.9) THEN 'Near Budget Limit (90+)'
                WHEN SUM(UT.amount) > (B.budget_amount * 0.8) THEN 'Approaching Budget Limit (80+)'
                ELSE 'Within Budget'
            END AS alert
        FROM PFT.USER_TRANSACTIONS UT 
        JOIN PFT.EXPENSE_CATEGORY C ON UT.category_id = C.id 
        LEFT JOIN PFT.BUDGET B ON B.category_id = UT.category_id 
            AND B.user_id = UT.user_id 
            AND B.budget_month = TO_CHAR(UT.transaction_date, 'YYYY-MM')
        WHERE UT.user_id = %s AND UT.transaction_type = 'expense' 
        GROUP BY TO_CHAR(UT.transaction_date, 'YYYY-MM'), C.name, B.budget_amount
        ORDER BY C.name 
        LIMIT %s OFFSET %s
        """
        result = await async_db_manager.execute_query_async(
            get_gcm_query, 
            (user_id, limit, (page - 1) * limit)
        )
        
        return {
            "success": True,
            "message": "Category monthly report retrieved successfully",
            "data": list(map(lambda x: {
                "month": x[0], 
                "category": x[1], 
                "expense": f"${x[2]}",
                "budget_amount": f"${x[3]}" if x[3] is not None else "$0",
                "alert": x[4] if x[3] is not None else "No Budget Set"
            }, result))
        }
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def get_gtbm(request, month):
    try:
        user_id = request.state.current_user
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
        result = await async_db_manager.execute_query_one_async(get_gtbm_query, (user_id, month))
        
        transaction_query = "SELECT * FROM PFT.USER_TRANSACTIONS WHERE user_id = %s AND TO_CHAR(transaction_date, 'YYYY-MM') = %s"
        transactions_data = await async_db_manager.execute_query_async(transaction_query, (user_id, month))
        
        if result:
            return {
                "success": True,
                "message": "Monthly transaction summary retrieved successfully",
                "data": {
                    "month": result[0],
                    "net_total": f"${result[1]}",
                    "total_income": f"${result[2]}",
                    "total_expenses": f"${result[3]}",
                    "transaction_count": result[4]
                },
                "transactions":{
                    "data": list(map(lambda x: {
                        "id": x[0],
                        "amount": f"${x[1]}",
                        "description": x[2],
                        "transaction_type": x[3],
                        "category_id": x[4],
                        "user_id": x[5],
                        "transaction_date": x[6]
                    }, transactions_data))
                }
            }
        else:
            raise HTTPException(status_code=404, detail="No data found for the specified month")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))