import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator

from app.models.pot import PotPriority


class PotBase(BaseModel):
    title: str = Field(..., max_length=120)
    target_amount: Decimal = Field(..., gt=0)
    current_amount: Decimal = Field(Decimal("0.00"), ge=0)
    target_date: date
    priority: PotPriority = PotPriority.MEDIUM


class PotCreate(PotBase):
    @field_validator("target_date")
    @classmethod
    def target_date_must_be_in_future(cls, v: date) -> date:
        if v < date.today():
            raise ValueError("Target date cannot be in the past")
        return v


class PotUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=120)
    target_amount: Optional[Decimal] = Field(None, gt=0)
    current_amount: Optional[Decimal] = Field(None, ge=0)
    target_date: Optional[date] = None
    priority: Optional[PotPriority] = None

    @field_validator("target_date")
    @classmethod
    def target_date_must_be_in_future(cls, v: Optional[date]) -> Optional[date]:
        if v and v < date.today():
            raise ValueError("Target date cannot be in the past")
        return v


class PotInDB(PotBase):
    id: uuid.UUID
    user_id: uuid.UUID
    progress_percentage: float
    remaining_amount: Decimal

    model_config = ConfigDict(from_attributes=True)
