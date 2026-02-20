from typing import List
from pydantic import BaseModel


class TagStat(BaseModel):
    name: str
    slug: str
    posts_count: int


class Stats(BaseModel):
    total_posts: int
    total_comments: int
    popular_tags: List[TagStat]