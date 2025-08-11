from fastapi import APIRouter,Request
import sys
import os
from models.transactions import Transaction, TransactionUpdate, SearchQuery
from controllers.transactions import (
    create_transaction as create_transaction_controller,
    update_transaction as update_transaction_controller,
    delete_transaction as delete_transaction_controller,
    list_transactions as list_transactions_controller,
    get_transaction as get_transaction_controller,
    search_transactions as search_transactions_controller
)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

router = APIRouter()

@router.post("/add")
def create_transaction(transaction: Transaction, request: Request):
    return create_transaction_controller(transaction, request)

@router.patch("/update/{transaction_id}")
def update_transaction(transaction_id: int, transaction: TransactionUpdate, request: Request):
    return update_transaction_controller(transaction_id, transaction, request)

@router.delete("/delete/{transaction_id}")
def delete_transaction(transaction_id: int, request: Request):
    return delete_transaction_controller(transaction_id, request)

@router.get("/list")
def list_transactions(request: Request, page: int = 1, limit: int = 10):
    return list_transactions_controller(request, page, limit)

@router.get("/get/{transaction_id}")
def get_transaction(transaction_id: int, request: Request):
    return get_transaction_controller(transaction_id, request)

@router.get("/search/{field}")
def search_transactions(field: str, search_query: SearchQuery, request: Request, page: int = 1, limit: int = 10):
    print(f"Searching transactions with field: {field} and query: {search_query}")
    return search_transactions_controller(field, search_query, request, page, limit)
