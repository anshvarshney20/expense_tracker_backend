from datetime import date
from decimal import Decimal
from typing import Optional
import uuid
from app.db.base import Base

class Expense(Base):
    __tablename__ = "expenses"

    user_id: uuid.UUID
    title: str
    amount: Decimal
    category: str
    emotion: Optional[str] = None
    is_avoidable: bool = False
    date: date
