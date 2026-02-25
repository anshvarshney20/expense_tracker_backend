import uuid
from decimal import Decimal
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ForbiddenError, ValidationError
from app.models.pot import Pot
from app.repositories.pot import PotRepository
from app.schemas.pot import PotCreate, PotUpdate


class PotService:
    def __init__(self, db: AsyncSession):
        self.pot_repo = PotRepository(db)

    async def create_pot(self, user_id: uuid.UUID, pot_in: PotCreate) -> Pot:
        obj_in = pot_in.model_dump()
        obj_in["user_id"] = user_id
        return await self.pot_repo.create(obj_in=obj_in)

    async def get_pot(self, pot_id: uuid.UUID, user_id: uuid.UUID) -> Pot:
        pot = await self.pot_repo.get(pot_id)
        if not pot:
            raise NotFoundError(message="Pot not found")
        if pot.user_id != user_id:
            raise ForbiddenError(message="Not authorized to access this pot")
        return pot

    async def get_pots(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> Sequence[Pot]:
        return await self.pot_repo.get_multi_by_user(
            user_id=user_id, skip=skip, limit=limit
        )

    async def update_pot(
        self, pot_id: uuid.UUID, user_id: uuid.UUID, pot_in: PotUpdate
    ) -> Pot:
        pot = await self.get_pot(pot_id, user_id)
        update_data = pot_in.model_dump(exclude_unset=True)
        
        # Prevent current_amount from exceeding target_amount
        if "current_amount" in update_data:
            new_amount = update_data["current_amount"]
            if new_amount > pot.target_amount:
                raise ValidationError(
                    message=f"Total amount cannot exceed your goal of {pot.target_amount}",
                    data={"target_amount": float(pot.target_amount)}
                )

        return await self.pot_repo.update(db_obj=pot, obj_in=update_data)

    async def delete_pot(self, pot_id: uuid.UUID, user_id: uuid.UUID) -> None:
        await self.get_pot(pot_id, user_id)
        await self.pot_repo.remove(id=pot_id)

    @staticmethod
    def calculate_progress(pot: Pot) -> dict:
        progress = (
            float(pot.current_amount / pot.target_amount * 100)
            if pot.target_amount > 0
            else 0.0
        )
        remaining = pot.target_amount - pot.current_amount
        return {
            "progress_percentage": min(max(progress, 0.0), 100.0),
            "remaining_amount": max(remaining, Decimal("0.00")),
        }
