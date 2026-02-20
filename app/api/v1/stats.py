from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.api.schemas.stats import Stats, TagStat
from app.domain.stats import service as stats_service

router = APIRouter()


@router.get("/stats/", response_model=Stats)
def get_stats(db: Session = Depends(get_db)):
    total_posts, total_comments, tag_rows = stats_service.get_stats(db)

    popular_tags = [
        TagStat(name=name, slug=slug, posts_count=posts_count)
        for (_id, name, slug, posts_count) in tag_rows
    ]

    return Stats(
        total_posts=total_posts,
        total_comments=total_comments,
        popular_tags=popular_tags,
    )