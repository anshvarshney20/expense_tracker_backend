import uuid
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api import deps
from app.models.user import User
from app.schemas.expense import (
    ExpenseCreate, 
    ExpenseUpdate, 
    ExpenseInDB, 
    ExpenseSummary,
    ExpenseList
)
from app.schemas.responses import SuccessResponse
from app.services.expense import ExpenseService

router = APIRouter()

@router.post("", response_model=SuccessResponse[ExpenseInDB])
async def create_expense(
    expense_in: ExpenseCreate,
    db: AsyncIOMotorDatabase = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    service = ExpenseService(db)
    expense = await service.create_expense(current_user.id, expense_in)
    return SuccessResponse(data=ExpenseInDB.model_validate(expense))

@router.get("", response_model=SuccessResponse[ExpenseList])
async def list_expenses(
    category: Optional[str] = None,
    avoidable: Optional[bool] = None,
    search_query: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("date"),
    sort_order: int = Query(-1, ge=-1, le=1),
    db: AsyncIOMotorDatabase = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    service = ExpenseService(db)
    result = await service.get_expenses(
        user_id=current_user.id,
        category=category,
        avoidable=avoidable,
        search_query=search_query,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return SuccessResponse(data=ExpenseList.model_validate(result))

@router.get("/summary", response_model=SuccessResponse[ExpenseSummary])
async def get_summary(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    db: AsyncIOMotorDatabase = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    service = ExpenseService(db)
    summary = await service.get_monthly_summary(current_user.id, year, month)
    return SuccessResponse(data=ExpenseSummary(**summary))

@router.get("/{expense_id}", response_model=SuccessResponse[ExpenseInDB])
async def get_expense(
    expense_id: uuid.UUID,
    db: AsyncIOMotorDatabase = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    service = ExpenseService(db)
    expense = await service.get_expense(expense_id, current_user.id)
    return SuccessResponse(data=ExpenseInDB.model_validate(expense))

@router.patch("/{expense_id}", response_model=SuccessResponse[ExpenseInDB])
async def update_expense(
    expense_id: uuid.UUID,
    expense_in: ExpenseUpdate,
    db: AsyncIOMotorDatabase = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    service = ExpenseService(db)
    expense = await service.update_expense(expense_id, current_user.id, expense_in)
    return SuccessResponse(data=ExpenseInDB.model_validate(expense))

@router.delete("/{expense_id}", response_model=SuccessResponse[None])
async def delete_expense(
    expense_id: uuid.UUID,
    db: AsyncIOMotorDatabase = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    service = ExpenseService(db)
    await service.delete_expense(expense_id, current_user.id)
    return SuccessResponse(message="Expense deleted successfully")
