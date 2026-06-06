"""Основной роутер API v1."""
from fastapi import APIRouter
from app.presentation.api.v1 import articles, evaluations, reviews

api_router = APIRouter(prefix="/api/v1")

# Подключаем роутеры
api_router.include_router(articles.router)
api_router.include_router(evaluations.router)
api_router.include_router(reviews.router)


@api_router.get("/health")
async def health_check():
    """Проверка здоровья API."""
    return {"status": "ok", "message": "API is running"}

