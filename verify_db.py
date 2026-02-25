import asyncio
from app.core import security
from app.db.session import AsyncSessionLocal
from app.models.base import User, Expense, Pot
from sqlalchemy import select

async def test_auth():
    email = "testuser@example.com"
    password = "StrongPassword123!"
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            print("User not found")
            return
            
        print(f"User email: {user.email}")
        print(f"Stored hash: {user.hashed_password}")
        
        is_valid = security.verify_password(password, user.hashed_password)
        print(f"Password valid: {is_valid}")

if __name__ == "__main__":
    asyncio.run(test_auth())
