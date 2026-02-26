from app.repositories.base import BaseRepository
from app.models.category import Category
import uuid
from typing import Sequence

class CategoryRepository(BaseRepository[Category]):
    async def get_by_user(self, user_id: uuid.UUID) -> Sequence[Category]:
        cursor = self.collection.find({"user_id": str(user_id)})
        docs = await cursor.to_list(length=100)
        return [self.model(**doc) for doc in docs]

    async def get_by_name(self, user_id: uuid.UUID, name: str) -> Category | None:
        doc = await self.collection.find_one({"user_id": str(user_id), "name": name})
        if doc:
            return self.model(**doc)
        return None
