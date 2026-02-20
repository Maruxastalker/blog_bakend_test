from typing import List, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.domain.posts.models import Post, post_tags_table
from app.domain.comments.models import Comment
from app.domain.tags.models import Tag


def get_stats(db: Session, popular_tags_limit: int = 5):
    total_posts = db.query(func.count(Post.id)).scalar() or 0
    total_comments = db.query(func.count(Comment.id)).scalar() or 0

    tag_rows: List[Tuple[int, str, str, int]] = (
        db.query(
            Tag.id,
            Tag.name,
            Tag.slug,
            func.count(Post.id).label("posts_count"),
        )
        .select_from(Tag)
        .join(post_tags_table, Tag.id == post_tags_table.c.tag_id)
        .join(Post, Post.id == post_tags_table.c.post_id)
        .filter(Post.status == "published")
        .group_by(Tag.id, Tag.name, Tag.slug)
        .order_by(func.count(Post.id).desc())
        .limit(popular_tags_limit)
        .all()
    )

    return total_posts, total_comments, tag_rows