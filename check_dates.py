
import asyncio
import os
import sys
from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Ensure we can import app
sys.path.append(os.getcwd())

from app.models.expense import Expense

DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def check_dates():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Expense))
        expenses = res.scalars().all()
        print(f"DIAGNOSTIC: Found {len(expenses)} expenses")
        for e in expenses:
            print(f"ID: {e.id}, Date: {e.date} (type: {type(e.date)}), Amount: {e.amount}, Title: {e.title}")
            
        # Also check current month summary for the first user found
        if expenses:
            uid = expenses[0].user_id
            year, month = 2026, 2
            start_date = date(year, month, 1)
            end_date = date(year, month + 1, 1) if month < 12 else date(year + 1, 1, 1)
            
            from sqlalchemy import and_, func
            query = select(
                func.sum(Expense.amount),
                func.count(Expense.id)
            ).where(
                and_(
                    Expense.user_id == uid,
                    Expense.date >= start_date,
                    Expense.date < end_date
                )
            )
            res = await db.execute(query)
            summary = res.first()
            print(f"DIAGNOSTIC: Summary for Feb 2026 for user {uid}: {summary}")

if __name__ == "__main__":
    asyncio.run(check_dates())
