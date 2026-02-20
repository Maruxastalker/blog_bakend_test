REST API для блог‑платформы с пользователями, статьями, комментариями и тегами.

## Краткое описание

Функциональность:

- Регистрация и вход пользователей (JWT‑аутентификация, bcrypt‑хеширование паролей).
- Статьи:
  - статусы: draft / published;
  - теги (M2M Post–Tag);
  - счётчик просмотров (увеличивается при просмотре детальной статьи);
  - пагинация, фильтрация по автору и тегу.
- Комментарии:
  - древовидная структура (parent_id);
  - только для авторизованных пользователей;
  - XSS‑защита (экранирование HTML).
- Поиск статей: `GET /api/search/?q=...` (LIKE по title + content).
- Статистика: `GET /api/stats/` (кол-во постов, кол-во комментариев, популярные теги).
- Загрузка файлов:
  - аватар пользователя;
  - изображения для статей (ссылки для вставки в Markdown).

Технологии:

- Python 3.11
- FastAPI
- SQLAlchemy + Alembic
- PostgreSQL
- Pydantic v2 + pydantic-settings
- Passlib[bcrypt] + python-jose (JWT)
- Pytest
- Docker + Docker Compose

---

## Установка и запуск (через Docker)

### Требования

- Docker
- Docker Compose

### 1. Клонирование

```bash
git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ>.git
cd backend_blog_testing

docker-compose build

docker-compose up -d db

docker-compose ps


Миграции:

1. Зайти в контейнер web:


docker-compose run --rm web bash
Ты окажешься внутри (root@...:/app#), рабочая директория /app.

2. Посмотреть миграции:

ls alembic/versions
3. Создать миграцию (если нужно):

alembic revision --autogenerate -m "init"
4. Применить миграции:

alembic upgrade head
5. Выйти:

exit