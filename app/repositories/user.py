from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.user import User
from app.repositories.base import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> User | None:
        doc = await self.collection.find_one({"email": email})
        if doc:
            return User(**doc)
        return None
