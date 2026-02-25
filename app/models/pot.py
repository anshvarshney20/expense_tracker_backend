from datetime import date
from decimal import Decimal
import enum
import uuid
from app.db.base import Base

class PotPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Pot(Base):
    __tablename__ = "pots"

    user_id: uuid.UUID
    title: str
    target_amount: Decimal
    current_amount: Decimal = Decimal("0.00")
    target_date: date
    priority: PotPriority = PotPriority.MEDIUM
