from fastapi import Depends, FastAPI
from middleware.validate import validate_jwt_middleware
from .auth import router as auth_router
from .user import router as user_router
from .expenses_category import router as expenses_category_router
from .transactions import router as transactions_router
from .budgets import router as budgets_router
from .reports import router as reports_router


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome to the Personal Finance Tracker API"}
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
@app.middleware("http")
async def add_jwt_validation_middleware(request, call_next):
    return await validate_jwt_middleware(request, call_next)
app.include_router(user_router, prefix="/users", tags=["user management"])
app.include_router(expenses_category_router, prefix="/expenses-category", tags=["expense category management"])
app.include_router(transactions_router, prefix="/transactions", tags=["transaction management"])
app.include_router(budgets_router, prefix="/budgets", tags=["budget management"])
app.include_router(reports_router, prefix="/reports", tags=["report generation"])



