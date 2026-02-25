import asyncio
from app.db.session import AsyncSessionLocal
from app.models.base import User
from sqlalchemy import select

async def list_users():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User))
        users = result.scalars().all()
        print(f"Total users: {len(users)}")
        for u in users:
            print(f"Email: {u.email}, ID: {u.id}")

if __name__ == "__main__":
    asyncio.run(list_users())
