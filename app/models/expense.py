import uuid
from datetime import date
from decimal import Decimal
from sqlalchemy import String, Numeric, ForeignKey, Boolean, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    emotion: Mapped[str] = mapped_column(String(50), nullable=True)
    is_avoidable: Mapped[bool] = mapped_column(Boolean, default=False)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    user: Mapped["User"] = relationship("User", back_populates="expenses")
