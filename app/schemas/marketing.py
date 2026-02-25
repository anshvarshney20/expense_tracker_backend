
from pydantic import BaseModel, EmailStr
from typing import Optional

class ContactCreate(BaseModel):
    name: str
    email: EmailStr
    interest: str
    message: str

class NewsletterSubscribe(BaseModel):
    email: EmailStr
