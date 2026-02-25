import uuid
import enum
from datetime import date
from decimal import Decimal
from sqlalchemy import String, Numeric, ForeignKey, Date, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PotPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Pot(Base):
    __tablename__ = "pots"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    target_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    current_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=Decimal("0.00"), nullable=False
    )
    target_date: Mapped[date] = mapped_column(Date, nullable=False)
    priority: Mapped[PotPriority] = mapped_column(
        Enum(PotPriority), default=PotPriority.MEDIUM, nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="pots")
