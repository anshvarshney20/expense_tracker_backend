import uuid
from typing import Sequence
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.pot import Pot
from app.repositories.base import BaseRepository

class PotRepository(BaseRepository[Pot]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(Pot, db)

    async def get_multi_by_user(
        self, *, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> Sequence[Pot]:
        cursor = (
            self.collection.find({"user_id": str(user_id)})
            .skip(skip)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        return [Pot(**doc) for doc in docs]
