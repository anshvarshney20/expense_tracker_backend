from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid
from typing import Sequence
from app.models.category import Category
from app.repositories.category import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.core.exceptions import NotFoundError, ForbiddenError

class CategoryService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.category_repo = CategoryRepository(Category, db)

    async def get_categories(self, user_id: uuid.UUID) -> Sequence[Category]:
        # Return user's categories. We could also include default categories here.
        return await self.category_repo.get_by_user(user_id)

    async def create_category(self, user_id: uuid.UUID, category_in: CategoryCreate) -> Category:
        # Check if category with same name already exists
        existing = await self.category_repo.get_by_name(user_id, category_in.name)
        if existing:
            return existing
            
        obj_in = category_in.model_dump()
        obj_in["user_id"] = str(user_id)
        obj_in["is_default"] = False
        return await self.category_repo.create(obj_in=obj_in)

    async def update_category(
        self, category_id: uuid.UUID, user_id: uuid.UUID, category_in: CategoryUpdate
    ) -> Category:
        category = await self.category_repo.get(category_id)
        if not category:
            raise NotFoundError(message="Category not found")
        if str(category.user_id) != str(user_id):
            raise ForbiddenError(message="Not authorized to update this category")
        
        update_data = category_in.model_dump(exclude_unset=True)
        return await self.category_repo.update(db_obj=category, obj_in=update_data)

    async def delete_category(self, category_id: uuid.UUID, user_id: uuid.UUID) -> None:
        category = await self.category_repo.get(category_id)
        if not category:
            raise NotFoundError(message="Category not found")
        if str(category.user_id) != str(user_id):
            raise ForbiddenError(message="Not authorized to delete this category")
        if category.is_default:
            raise ForbiddenError(message="Cannot delete default categories")
            
        await self.category_repo.remove(id=category_id)
