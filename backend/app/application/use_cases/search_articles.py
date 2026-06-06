"""Use case для поиска статей через orchestration layer."""
from typing import List

from app.application.dto.article_dto import ArticleSearchResultDTO
from app.application.services.orchestration_service import OrchestrationService


class SearchArticlesUseCase:
    """Use case для поиска статей через CoordinatorAgent."""

    def __init__(self, orchestration_service: OrchestrationService):
        self.orchestration_service = orchestration_service

    async def execute(self, query: str, max_results: int = 10) -> List[ArticleSearchResultDTO]:
        return await self.orchestration_service.search_articles(query, max_results)
