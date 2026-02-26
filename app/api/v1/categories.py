from fastapi import APIRouter, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
import uuid

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryInDB
from app.services.category import CategoryService

from app.schemas.responses import SuccessResponse

router = APIRouter()

@router.get("", response_model=SuccessResponse[List[CategoryInDB]])
async def get_categories(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = CategoryService(db)
    categories = await service.get_categories(current_user.id)
    return SuccessResponse(data=[CategoryInDB.model_validate(c) for c in categories])

@router.post("", response_model=SuccessResponse[CategoryInDB], status_code=status.HTTP_201_CREATED)
async def create_category(
    category_in: CategoryCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = CategoryService(db)
    category = await service.create_category(current_user.id, category_in)
    return SuccessResponse(data=CategoryInDB.model_validate(category))

@router.patch("/{category_id}", response_model=SuccessResponse[CategoryInDB])
async def update_category(
    category_id: uuid.UUID,
    category_in: CategoryUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = CategoryService(db)
    category = await service.update_category(category_id, current_user.id, category_in)
    return SuccessResponse(data=CategoryInDB.model_validate(category))

@router.delete("/{category_id}", response_model=SuccessResponse[None])
async def delete_category(
    category_id: uuid.UUID,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = CategoryService(db)
    await service.delete_category(category_id, current_user.id)
    return SuccessResponse(message="Category deleted successfully")
