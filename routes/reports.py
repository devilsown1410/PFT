from fastapi import APIRouter,Request
import sys
import os
from controllers.reports import get_gcm as get_gcm_controller, get_gtbm as get_gtbm_controller

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

router = APIRouter()

@router.get("/gcm")
def get_gcm(request: Request, page: int = 1, limit: int = 10):
    return get_gcm_controller(request, page, limit)

@router.get("/gtbm/{month}")
def get_gtbm(request: Request, month: str):
    return get_gtbm_controller(request, month)