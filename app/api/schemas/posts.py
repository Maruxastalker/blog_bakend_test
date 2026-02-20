from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from .comments import CommentRead
from .tags import TagRead
from .users import UserPublic


class PostBase(BaseModel):
    title: str
    content: str = Field(..., min_length=100)
    status: str = Field("draft", pattern="^(draft|published)$")
    tags: List[str] = []


class PostCreate(PostBase):
    slug: Optional[str] = None


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = Field(None, min_length=100)
    status: Optional[str] = Field(None, pattern="^(draft|published)$")
    tags: Optional[List[str]] = None


class PostListItem(BaseModel):
    title: str
    slug: str
    author: str
    created_at: datetime
    excerpt: str


class PostDetail(BaseModel):
    id: int
    title: str
    slug: str
    content: str
    status: str
    created_at: datetime
    updated_at: datetime
    view_count: int
    author: UserPublic
    tags: List[TagRead]
    comments: List[CommentRead]

    class Config:
        from_attributes = True