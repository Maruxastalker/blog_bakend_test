from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.schemas.posts import (
    PostCreate,
    PostDetail,
    PostListItem,
    PostUpdate,
)
from app.core.db import get_db
from app.domain.posts import service as post_service
from app.core.cache import posts_cache  
from app.domain.posts.models import Post
from app.domain.users.models import User

router = APIRouter()

POSTS_CACHE_TTL = 300

@router.get("/posts/", response_model=List[PostListItem])
def list_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    tag: Optional[str] = None,
    author: Optional[str] = None,
    db: Session = Depends(get_db),
):
    cache_key = f"posts:{page}:{page_size}:{tag or ''}:{author or ''}"
    cached = posts_cache.get(cache_key)
    if cached is not None:
        return cached

    posts = post_service.list_published_posts(
        db,
        page=page,
        page_size=page_size,
        tag_slug=tag,
        author_username=author,
    )
    result = [
        PostListItem(
            title=p.title,
            slug=p.slug,
            author=p.author.username,
            created_at=p.created_at,
            excerpt=p.content[:200],
        )
        for p in posts
    ]

    posts_cache.set(cache_key, result, POSTS_CACHE_TTL)
    return result


@router.get("/posts/{slug}/", response_model=PostDetail)
def get_post_detail(slug: str, db: Session = Depends(get_db)):
    post = post_service.get_published_post_by_slug(db, slug)
    post_service.increase_view_count(db, post)
    return post


@router.post("/posts/", response_model=PostDetail, status_code=status.HTTP_201_CREATED)
def create_post(
    post_in: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = post_service.create_post(
        db,
        author=current_user,
        title=post_in.title,
        content=post_in.content,
        status=post_in.status,
        tag_names=post_in.tags,
        slug=post_in.slug,
    )
    posts_cache.clear(prefix="posts:")
    return post


@router.put("/posts/{slug}/", response_model=PostDetail)
def update_post(
    slug: str,
    post_in: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = post_service.get_post_by_slug_for_edit(db, slug)
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    post = post_service.update_post(
        db,
        post=post,
        title=post_in.title,
        content=post_in.content,
        status=post_in.status,
        tag_names=post_in.tags,
    )
    posts_cache.clear(prefix="posts:")
    return post


@router.delete("/posts/{slug}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = post_service.get_post_by_slug_for_edit(db, slug)
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    post_service.delete_post(db, post)
    posts_cache.clear(prefix="posts:")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/search/", response_model=List[PostListItem])
def search_posts(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    posts = post_service.search_posts(
        db, query=q, page=page, page_size=page_size
    )
    return [
        PostListItem(
            title=p.title,
            slug=p.slug,
            author=p.author.username,
            created_at=p.created_at,
            excerpt=p.content[:200],
        )
        for p in posts
    ]