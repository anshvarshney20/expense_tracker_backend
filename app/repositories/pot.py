import uuid
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.pot import Pot
from app.repositories.base import BaseRepository


class PotRepository(BaseRepository[Pot]):
    def __init__(self, db: AsyncSession):
        super().__init__(Pot, db)

    async def get_multi_by_user(
        self, *, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> Sequence[Pot]:
        query = (
            select(Pot)
            .where(Pot.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()
