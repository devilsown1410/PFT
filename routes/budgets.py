from fastapi import APIRouter,Request
import sys
import os
from controllers.budgets import (
    create_budget as create_budget_controller, 
    update_budget as update_budget_controller,
    list_budgets as list_budgets_controller
    )
from models.budget import Budget, BudgetUpdate

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

router = APIRouter()

@router.post("/add")
def create_budget(budget: Budget, request: Request):
    return create_budget_controller(budget, request)

@router.patch("/update/{budget_id}")
def update_budget(budget_id: int, budget: BudgetUpdate, request: Request):
    return update_budget_controller(budget_id, budget, request)

@router.get("/list")
def list_budgets(request: Request, page: int = 1, limit: int = 10):
    return list_budgets_controller(request, page, limit)