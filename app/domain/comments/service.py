from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.utils import sanitize_comment_text
from app.domain.posts.models import Post
from app.domain.users.models import User
from .models import Comment


def list_comments_for_post(db: Session, post: Post) -> List[Comment]:
    return (
        db.query(Comment)
        .options(joinedload(Comment.author))
        .filter(Comment.post_id == post.id)
        .order_by(Comment.created_at)
        .all()
    )


def add_comment_to_post(
    db: Session,
    post: Post,
    author: User,
    text: str,
    parent_id: Optional[int] = None,
) -> Comment:
    if parent_id is not None:
        parent = (
            db.query(Comment)
            .filter(Comment.id == parent_id, Comment.post_id == post.id)
            .first()
        )
        if not parent:
            raise HTTPException(status_code=400, detail="Invalid parent_id")

    safe_text = sanitize_comment_text(text)

    comment = Comment(
        post_id=post.id,
        author_id=author.id,
        text=safe_text,
        parent_id=parent_id,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def get_comment_with_post(db: Session, comment_id: int) -> Comment:
    comment = (
        db.query(Comment)
        .options(joinedload(Comment.post))
        .filter(Comment.id == comment_id)
        .first()
    )
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


def delete_comment(db: Session, comment: Comment) -> None:
    db.delete(comment)
    db.commit()