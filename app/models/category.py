from app.db.base import Base
import uuid
from typing import Optional

class Category(Base):
    __tablename__ = "categories"

    user_id: uuid.UUID
    name: str
    icon: Optional[str] = "Tag"
    color: Optional[str] = "#3b82f6"
    is_default: bool = False
