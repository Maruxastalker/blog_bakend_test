from fastapi import APIRouter

from app.api.v1 import auth, users, posts, comments

api_router = APIRouter(prefix="/api")

api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(users.router, tags=["users"])
api_router.include_router(posts.router, tags=["posts"])
api_router.include_router(comments.router, tags=["comments"])