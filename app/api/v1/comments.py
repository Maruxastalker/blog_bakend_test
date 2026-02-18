from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.schemas.comments import CommentCreate, CommentRead
from app.core.db import get_db
from app.domain.comments import service as comment_service
from app.domain.users.models import User
from app.domain.posts import service as post_service

router = APIRouter()


@router.get("/posts/{slug}/comments/", response_model=List[CommentRead])
def get_post_comments(slug: str, db: Session = Depends(get_db)):
    post = post_service.get_published_post_by_slug(db, slug)
    comments = comment_service.list_comments_for_post(db, post)
    return comments


@router.post(
    "/posts/{slug}/comments/",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
)
def add_comment(
    slug: str,
    comment_in: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = post_service.get_published_post_by_slug(db, slug)
    comment = comment_service.add_comment_to_post(
        db,
        post=post,
        author=current_user,
        text=comment_in.text,
        parent_id=comment_in.parent_id,
    )
    return comment


@router.delete("/comments/{comment_id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = comment_service.get_comment_with_post(db, comment_id)
    if comment.author_id != current_user.id and comment.post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    comment_service.delete_comment(db, comment)
    return Response(status_code=status.HTTP_204_NO_CONTENT)