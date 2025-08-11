from fastapi import APIRouter,Request
from pydantic import BaseModel
import sys
import os
from models.expenses import Expense
from controllers.expenses_category import create_expense_category as create_expense_controller, edit_expense_category as edit_expense_controller, delete_expense_category as delete_expense_controller, list_expense_categories as list_expenses_controller, get_expense_category as get_expense_controller

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


router = APIRouter()

@router.post("/add")
def create_expense_category(expense: Expense, request: Request):
    return create_expense_controller(expense, request)

@router.put('/edit/{id}')
def edit_expense_category( expense: Expense, request: Request):
    return edit_expense_controller(expense, request)
    
@router.delete('/delete/{id}')
def delete_expense_category(request: Request):
    return delete_expense_controller(request)

@router.get('/list')
def list_expense_categories( request:Request):
    return list_expenses_controller(request)
    
@router.get('/get/{id}')
def get_expense_category(id: int, request: Request):
    return get_expense_controller(id, request)