"""Интерфейсы репозиториев."""
from app.domain.repositories.base import BaseRepository
from app.domain.repositories.article_repository import ArticleRepository
from app.domain.repositories.evaluation_repository import EvaluationRepository
from app.domain.repositories.review_repository import ReviewRepository

__all__ = [
    "BaseRepository",
    "ArticleRepository",
    "EvaluationRepository",
    "ReviewRepository"
]
