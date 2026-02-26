import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator


class ExpenseBase(BaseModel):
    title: str = Field(..., max_length=120)
    amount: Decimal = Field(..., gt=0)
    category: str = Field(..., max_length=50)
    emotion: Optional[str] = Field(None, max_length=50)
    is_avoidable: bool = False
    date: date


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=120)
    amount: Optional[Decimal] = Field(None, gt=0)
    category: Optional[str] = Field(None, max_length=50)
    emotion: Optional[str] = Field(None, max_length=50)
    is_avoidable: Optional[bool] = None
    date: Optional[date] = None


class ExpenseInDB(ExpenseBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExpenseSummary(BaseModel):
    total_amount: Decimal
    count: int
    lifetime_total: Decimal = Field(default=Decimal('0.00'))
    category_breakdown: dict[str, Decimal]

class ExpenseList(BaseModel):
    items: list[ExpenseInDB]
    total_count: int
    total_amount: Decimal
    total_avoidable_amount: Decimal
