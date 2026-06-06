"""Реализация репозиториев."""
from app.infrastructure.repositories.article_repository_impl import InMemoryArticleRepository
from app.infrastructure.repositories.evaluation_repository_impl import InMemoryEvaluationRepository
from app.infrastructure.repositories.review_repository_impl import InMemoryReviewRepository

__all__ = [
    "InMemoryArticleRepository",
    "InMemoryEvaluationRepository",
    "InMemoryReviewRepository"
]
