import uuid
from datetime import date
from typing import Sequence
from sqlalchemy import select, func, and_, String, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.expense import Expense
from app.repositories.base import BaseRepository


class ExpenseRepository(BaseRepository[Expense]):
    def __init__(self, db: AsyncSession):
        super().__init__(Expense, db)

    async def get_multi_by_user(
        self,
        *,
        user_id: uuid.UUID,
        category: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Expense]:
        query = select(Expense).where(Expense.user_id == user_id)
        
        if category:
            query = query.where(Expense.category == category)
        if start_date:
            query = query.where(Expense.date >= start_date)
        if end_date:
            query = query.where(Expense.date <= end_date)
            
        query = query.order_by(Expense.date.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_monthly_summary(
        self, user_id: uuid.UUID, year: int, month: int
    ) -> dict:
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)

        # Core spending aggregates with dialect-aware date filtering
        summary_query = select(
            func.sum(Expense.amount).label("total"),
            func.count(Expense.id).label("count")
        ).where(Expense.user_id == user_id)

        # Apply robust filtering based on dialect
        if self.db.bind.dialect.name == "sqlite":
            # SQLite ID comparison can be finicky with UUID objects in aggregates
            user_id_str = str(user_id)
            summary_query = summary_query.where(func.cast(Expense.user_id, String) == user_id_str)
            
            # Robust date matching
            month_pattern = f"{year}-{month:02d}%"
            month_pattern_alt = f"{year}-{month}%"
            summary_query = summary_query.where(
                or_(
                    func.cast(Expense.date, String).like(month_pattern),
                    func.cast(Expense.date, String).like(month_pattern_alt)
                )
            )
        else:
            summary_query = summary_query.where(
                and_(
                    Expense.user_id == user_id,
                    Expense.date >= start_date,
                    Expense.date < end_date
                )
            )

        res = await self.db.execute(summary_query)
        row = res.first()
        
        # Calculate lifetime total for absolute transparency
        lifetime_query = select(func.sum(Expense.amount))
        if self.db.bind.dialect.name == "sqlite":
            lifetime_query = lifetime_query.where(func.cast(Expense.user_id, String) == str(user_id))
        else:
            lifetime_query = lifetime_query.where(Expense.user_id == user_id)
            
        lifetime_res = await self.db.execute(lifetime_query)
        lifetime_total = lifetime_res.scalar() or 0

        # Category breakdown with matching filtered context
        cat_query = select(
            Expense.category,
            func.sum(Expense.amount).label("total")
        ).where(Expense.user_id == user_id)

        if self.db.bind.dialect.name == "sqlite":
            user_id_str = str(user_id)
            cat_query = cat_query.where(func.cast(Expense.user_id, String) == user_id_str)
            
            month_pattern = f"{year}-{month:02d}%"
            month_pattern_alt = f"{year}-{month}%"
            cat_query = cat_query.where(
                or_(
                    func.cast(Expense.date, String).like(month_pattern),
                    func.cast(Expense.date, String).like(month_pattern_alt)
                )
            )
        else:
            cat_query = cat_query.where(
                and_(
                    Expense.user_id == user_id,
                    Expense.date >= start_date,
                    Expense.date < end_date
                )
            )
        
        cat_query = cat_query.group_by(Expense.category)
        
        cat_res = await self.db.execute(cat_query)
        breakdown = {cat_row[0]: cat_row[1] for cat_row in cat_res.all()}
        
        return {
            "total_amount": row[0] if row and row[0] else 0,
            "count": row[1] if row and row[1] else 0,
            "lifetime_total": lifetime_total,
            "category_breakdown": breakdown
        }
