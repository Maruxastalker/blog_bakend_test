import re
from html import escape

from sqlalchemy.orm import Session

from app.domain.posts.models import Post


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "item"


def generate_unique_post_slug(db: Session, base_slug: str) -> str:
    slug = base_slug
    index = 1
    while db.query(Post).filter(Post.slug == slug).first() is not None:
        slug = f"{base_slug}-{index}"
        index += 1
    return slug


def sanitize_comment_text(text: str) -> str:
    # простая защита от XSS: экранируем HTML
    return escape(text)