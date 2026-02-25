import uuid
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    expenses: Mapped[list["Expense"]] = relationship(
        "Expense", back_populates="user", cascade="all, delete-orphan"
    )
    pots: Mapped[list["Pot"]] = relationship(
        "Pot", back_populates="user", cascade="all, delete-orphan"
    )
