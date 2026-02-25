import uuid
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None
    currency: str | None = "USD"


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None
    currency: str | None = None
    password: str | None = None


class UserInDB(UserBase):
    id: uuid.UUID
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
