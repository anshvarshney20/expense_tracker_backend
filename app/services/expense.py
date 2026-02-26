import uuid
from datetime import date
from typing import Sequence
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.exceptions import NotFoundError, ForbiddenError
from app.models.expense import Expense
from app.repositories.expense import ExpenseRepository
from app.schemas.expense import ExpenseCreate, ExpenseUpdate

class ExpenseService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.expense_repo = ExpenseRepository(db)

    async def create_expense(
        self, user_id: uuid.UUID, expense_in: ExpenseCreate
    ) -> Expense:
        obj_in = expense_in.model_dump()
        obj_in["user_id"] = str(user_id)
        return await self.expense_repo.create(obj_in=obj_in)

    async def get_expense(
        self, expense_id: uuid.UUID, user_id: uuid.UUID
    ) -> Expense:
        expense = await self.expense_repo.get(expense_id)
        if not expense:
            raise NotFoundError(message="Expense not found")
        if str(expense.user_id) != str(user_id):
            raise ForbiddenError(message="Not authorized to access this expense")
        return expense

    async def get_expenses(
        self,
        user_id: uuid.UUID,
        category: str | None = None,
        avoidable: bool | None = None,
        search_query: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "date",
        sort_order: int = -1,
    ) -> dict:
        expenses, total_count, total_amount, total_avoidable = await self.expense_repo.get_multi_by_user(
            user_id=user_id,
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
        return {
            "items": expenses,
            "total_count": total_count,
            "total_amount": total_amount,
            "total_avoidable_amount": total_avoidable
        }

    async def update_expense(
        self,
        expense_id: uuid.UUID,
        user_id: uuid.UUID,
        expense_in: ExpenseUpdate
    ) -> Expense:
        expense = await self.get_expense(expense_id, user_id)
        update_data = expense_in.model_dump(exclude_unset=True)
        return await self.expense_repo.update(db_obj=expense, obj_in=update_data)

    async def delete_expense(
        self, expense_id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        await self.get_expense(expense_id, user_id)
        await self.expense_repo.remove(id=expense_id)

    async def get_monthly_summary(
        self, user_id: uuid.UUID, year: int, month: int
    ) -> dict:
        return await self.expense_repo.get_monthly_summary(user_id, year, month)
