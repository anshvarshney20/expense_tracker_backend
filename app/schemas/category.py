from pydantic import BaseModel
import uuid
from typing import Optional
from datetime import datetime

class CategoryBase(BaseModel):
    name: str
    icon: Optional[str] = "Tag"
    color: Optional[str] = "#3b82f6"

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None

class CategoryInDB(CategoryBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    is_default: bool = False

    class Config:
        from_attributes = True
