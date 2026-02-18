from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.db import Base
from app.domain.posts.models import post_tags_table


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    slug = Column(String(50), unique=True, nullable=False)

    posts = relationship("Post", secondary=post_tags_table, back_populates="tags")