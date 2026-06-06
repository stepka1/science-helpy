"""Dependency injection для FastAPI."""
from app.domain.repositories.article_repository import ArticleRepository
from app.domain.repositories.evaluation_repository import EvaluationRepository
from app.domain.repositories.review_repository import ReviewRepository
from app.infrastructure.repositories import (
    InMemoryArticleRepository,
    InMemoryEvaluationRepository,
    InMemoryReviewRepository
)
from app.application.services.orchestration_service import OrchestrationService


# Создаем singleton экземпляры
_article_repository: ArticleRepository = InMemoryArticleRepository()
_evaluation_repository: EvaluationRepository = InMemoryEvaluationRepository()
_review_repository: ReviewRepository = InMemoryReviewRepository()
_orchestration_service = OrchestrationService()


def get_article_repository() -> ArticleRepository:
    """Получить репозиторий статей."""
    return _article_repository


def get_evaluation_repository() -> EvaluationRepository:
    """Получить репозиторий оценок."""
    return _evaluation_repository


def get_review_repository() -> ReviewRepository:
    """Получить репозиторий обзоров."""
    return _review_repository


def get_orchestration_service() -> OrchestrationService:
    """Получить orchestration service."""
    return _orchestration_service
