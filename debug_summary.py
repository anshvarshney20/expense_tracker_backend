
import asyncio
import uuid
from datetime import date
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Mocking parts of the app to run a quick test
DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def test_summary():
    async with AsyncSessionLocal() as db:
        # Get a user who has expenses
        res = await db.execute(select(func.count()).select_from(func.text("expenses")))
        print(f"Total expenses in db: {res.scalar()}")
        
        # Get the first expense's user_id and date
        res = await db.execute(func.text("SELECT user_id, date, amount FROM expenses LIMIT 1"))
        row = res.first()
        if not row:
            print("No expenses found")
            return
        
        user_id_str, expense_date_str, amount = row
        user_id = uuid.UUID(user_id_str)
        year = int(expense_date_str.split('-')[0])
        month = int(expense_date_str.split('-')[1])
        
        print(f"Testing for User: {user_id}, Month: {month}, Year: {year}")
        
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)
            
        print(f"Date range: {start_date} to {end_date}")
        
        # This matches the code in ExpenseRepository
        # We need the model for the actual select
        from app.models.expense import Expense
        
        query = select(
            func.sum(Expense.amount).label("total"),
            func.count(Expense.id).label("count")
        ).where(
            and_(
                Expense.user_id == user_id,
                Expense.date >= start_date,
                Expense.date < end_date
            )
        )
        
        res = await db.execute(query)
        summary_row = res.first()
        print(f"Summary result: {summary_row}")
        
if __name__ == "__main__":
    asyncio.run(test_summary())
