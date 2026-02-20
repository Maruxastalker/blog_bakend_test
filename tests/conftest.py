import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app as fastapi_app      # ← алиас, чтобы не затереть
from app.core.db import Base, get_db
import app.domain as _domain  # noqa: F401  # просто чтобы модели подгрузились

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


@pytest.fixture(autouse=True)
def setup_db():
    """Чистим все таблицы перед каждым тестом."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def override_get_db():
    """Заменяем зависимость get_db, чтобы тесты ходили в SQLite, а не в PostgreSQL."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# override делаем на FastAPI-приложении
fastapi_app.dependency_overrides[get_db] = override_get_db


@pytest.fixture()
def client():
    """Клиент для запросов к API в тестах."""
    return TestClient(fastapi_app)