from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@db:5432/blog"
    SECRET_KEY: str = "CHANGE_ME"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    MEDIA_ROOT: str = "media"
    AVATARS_SUBDIR: str = "avatars"
    POST_IMAGES_SUBDIR: str = "posts"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()