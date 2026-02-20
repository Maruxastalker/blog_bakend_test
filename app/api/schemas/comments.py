from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    parent_id: Optional[int] = None


class CommentAuthor(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class CommentRead(BaseModel):
    id: int
    text: str
    created_at: datetime
    parent_id: Optional[int]
    author: CommentAuthor

    class Config:
        from_attributes = True