from app.db.base import Base
from typing import Optional

class User(Base):
    __tablename__ = "users"

    email: str
    hashed_password: str
    full_name: Optional[str] = None
    currency: str = "USD"
    is_active: bool = True
