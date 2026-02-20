from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from sqlalchemy.orm import Session

from app.api.schemas.posts import PostListItem
from app.api.schemas.users import UserPublic
from app.core.db import get_db
from app.domain.posts.models import Post
from app.domain.users.models import User
from app.domain.users.service import get_user_by_username
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/users/", response_model=List[UserPublic])
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    users = (
        db.query(User)
        .order_by(User.date_joined.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return users


@router.get("/users/{username}/", response_model=UserPublic)
def get_user_profile(username: str, db: Session = Depends(get_db)):
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/users/{username}/posts/", response_model=List[PostListItem])
def get_user_posts(
    username: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    query = (
        db.query(Post)
        .filter(Post.author_id == user.id, Post.status == "published")
        .order_by(Post.created_at.desc())
    )
    posts = query.offset((page - 1) * page_size).limit(page_size).all()

    return [
        PostListItem(
            title=p.title,
            slug=p.slug,
            author=user.username,
            created_at=p.created_at,
            excerpt=p.content[:200],
        )
        for p in posts
    ]

@router.post("/users/{username}/avatar/", response_model=UserPublic)
def upload_avatar(
    username: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.username != username:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    avatar_url = save_avatar_file(file, user.id)
    user.avatar_url = avatar_url
    db.add(user)
    db.commit()
    db.refresh(user)
    return user