from datetime import datetime

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    date_joined: datetime
    is_active: bool
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True