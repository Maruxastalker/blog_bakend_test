from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from app.core.utils import generate_unique_post_slug, slugify
from app.domain.comments.models import Comment
from app.domain.tags.models import Tag
from app.domain.users.models import User
from .models import Post


def list_published_posts(
    db: Session,
    page: int,
    page_size: int,
    tag_slug: Optional[str] = None,
    author_username: Optional[str] = None,
) -> List[Post]:
    query = db.query(Post).join(User).filter(Post.status == "published")

    if author_username:
        query = query.filter(User.username == author_username)
    if tag_slug:
        query = query.join(Post.tags).filter(Tag.slug == tag_slug)

    posts = (
        query.options(joinedload(Post.author))
        .order_by(Post.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return posts


def get_published_post_by_slug(db: Session, slug: str) -> Post:
    post = (
        db.query(Post)
        .options(
            joinedload(Post.author),
            joinedload(Post.tags),
            joinedload(Post.comments).joinedload(Comment.author),
        )
        .filter(Post.slug == slug, Post.status == "published")
        .first()
    )
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


def get_post_by_slug_for_edit(db: Session, slug: str) -> Post:
    post = (
        db.query(Post)
        .options(
            joinedload(Post.author),
            joinedload(Post.tags),
            joinedload(Post.comments).joinedload(Comment.author),
        )
        .filter(Post.slug == slug)
        .first()
    )
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


def increase_view_count(db: Session, post: Post) -> Post:
    post.view_count += 1
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def create_post(
    db: Session,
    author: User,
    title: str,
    content: str,
    status: str,
    tag_names: Optional[list[str]] = None,
    slug: Optional[str] = None,
) -> Post:
    base_slug = slug or slugify(title)
    unique_slug = generate_unique_post_slug(db, base_slug)

    post = Post(
        title=title,
        slug=unique_slug,
        content=content,
        status=status,
        author_id=author.id,
    )

    tags = []
    for name in tag_names or []:
        tag_slug = slugify(name)
        tag = db.query(Tag).filter(Tag.slug == tag_slug).first()
        if not tag:
            tag = Tag(name=name, slug=tag_slug)
            db.add(tag)
            db.flush()
        tags.append(tag)

    post.tags = tags
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def update_post(
    db: Session,
    post: Post,
    title: Optional[str] = None,
    content: Optional[str] = None,
    status: Optional[str] = None,
    tag_names: Optional[list[str]] = None,
) -> Post:
    if title is not None:
        post.title = title
    if content is not None:
        post.content = content
    if status is not None:
        post.status = status
    if tag_names is not None:
        tags = []
        for name in tag_names:
            tag_slug = slugify(name)
            tag = db.query(Tag).filter(Tag.slug == tag_slug).first()
            if not tag:
                tag = Tag(name=name, slug=tag_slug)
                db.add(tag)
                db.flush()
            tags.append(tag)
        post.tags = tags

    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def delete_post(db: Session, post: Post) -> None:
    db.delete(post)
    db.commit()


def search_posts(
    db: Session,
    query: str,
    page: int,
    page_size: int,
) -> List[Post]:
    pattern = f"%{query}%"
    posts = (
        db.query(Post)
        .join(User)
        .filter(
            Post.status == "published",
            or_(Post.title.ilike(pattern), Post.content.ilike(pattern)),
        )
        .options(joinedload(Post.author))
        .order_by(Post.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return posts