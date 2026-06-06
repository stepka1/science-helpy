"""Use case для парсинга статьи через orchestration layer."""
from uuid import UUID

from app.application.services.orchestration_service import OrchestrationService
from app.domain.repositories.article_repository import ArticleRepository
from app.shared.exceptions.base import NotFoundError


class ParseArticleUseCase:
    """Use case для парсинга содержимого статьи через agents_system."""

    def __init__(self, article_repository: ArticleRepository, orchestration_service: OrchestrationService):
        self.article_repository = article_repository
        self.orchestration_service = orchestration_service

    async def execute(self, article_id: UUID) -> str:
        article = await self.article_repository.get_by_id(article_id)
        if not article:
            raise NotFoundError(f"Article with ID {article_id} not found")
        if article.parsed_content:
            return article.parsed_content

        parsed_content = await self.orchestration_service.parse_article(article)
        article.parsed_content = parsed_content
        await self.article_repository.update(article)
        return parsed_content
