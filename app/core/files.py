from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from .config import settings

MEDIA_ROOT = Path(settings.MEDIA_ROOT)


def save_avatar_file(file: UploadFile, user_id: int) -> str:
    MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
    avatar_dir = MEDIA_ROOT / settings.AVATARS_SUBDIR
    avatar_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename or "").suffix or ".bin"
    filename = f"user_{user_id}_{uuid4().hex}{ext}"
    file_path = avatar_dir / filename

    with file_path.open("wb") as f:
        f.write(file.file.read())

    return f"/media/{settings.AVATARS_SUBDIR}/{filename}"


def save_post_image(file: UploadFile) -> str:
    MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
    img_dir = MEDIA_ROOT / settings.POST_IMAGES_SUBDIR
    img_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename or "").suffix or ".bin"
    filename = f"post_{uuid4().hex}{ext}"
    file_path = img_dir / filename

    with file_path.open("wb") as f:
        f.write(file.file.read())

    return f"/media/{settings.POST_IMAGES_SUBDIR}/{filename}"