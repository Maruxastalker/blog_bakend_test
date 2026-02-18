from fastapi import FastAPI

from app.api.router import api_router

app = FastAPI(title="Blog API (DDD-ish)")

app.include_router(api_router)