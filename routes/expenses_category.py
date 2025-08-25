from fastapi import APIRouter,Request
import sys
import os
from models.expenses import Expense
from controllers.expenses_category import create_expense_category as create_expense_controller, edit_expense_category as edit_expense_controller, delete_expense_category as delete_expense_controller, list_expense_categories as list_expenses_controller, get_expense_category as get_expense_controller

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


router = APIRouter()

@router.post("/add")
async def create_expense_category(expense: Expense, request: Request):
    return await create_expense_controller(expense, request)

@router.put('/edit/{id}')
async def edit_expense_category(expense: Expense, request: Request):
    return await edit_expense_controller(expense, request)
    
@router.delete('/delete/{id}')
async def delete_expense_category(request: Request):
    return await delete_expense_controller(request)

@router.get('/list')
async def list_expense_categories(request: Request, page: int = 1, limit: int = 10):
    return await list_expenses_controller(request, page, limit)
    
@router.get('/get/{id}')
async def get_expense_category(id: int, request: Request):
    return await get_expense_controller(id, request)